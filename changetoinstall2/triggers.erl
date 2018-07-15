-module(triggers).
-author("pedrolopes").

-include("querying.hrl").

-define(MAP_OP(Col, CRDT, CRDTOper, Val), {{Col, CRDT}, {CRDTOper, Val}}).
-define(COUNTER_TABLE, 'Counter').

%% API
-export([create_triggers/1,
         log_interfaces_trigger/1, log_interfaces_trigger/2,
         create_log_table/3]).

create_triggers(Updates) ->
    lists:foreach(fun(ObjUpdate) ->
        %% A bucket is analogous to a table.
        ?OBJECT_UPDATE(Key, Type, Bucket, _Op, _Param) = ObjUpdate,
        case update_type({Key, Type, Bucket}) of
            ?RECORD_UPD_TYPE ->
                case Bucket of
                    interfaces -> register_trigger(Bucket, log_interfaces_trigger);
                    ipvfourrib -> register_trigger(Bucket, log_interfaces_trigger);
                    interfaceneighbour -> register_trigger(Bucket, log_interfaces_trigger);
                    _ -> ok
                end;
            _ ->
                ok
        end
    end, Updates).

%% ====================================================================
%% Triggers
%% ====================================================================

log_interfaces_trigger(Update) when is_tuple(Update) ->
    {ok, TxId} = querying_utils:start_transaction(),
    {ok, Updates} = log_interfaces_trigger(Update, TxId),
    {ok, _} = querying_utils:commit_transaction(TxId),

    {ok, Updates}.

%% This is the trigger that will build the log table.
%% This function triggers for every update to the tables
%% 'interfaces' and 'ipvfourrib'.
log_interfaces_trigger(Update, Transaction) when is_tuple(Update) ->
    {{Key, Bucket}, Type, Param} = Update,
    LogUpdates = generate_log_updates(Key, Type, Bucket, Param, Transaction),
    IndexUpdates = lists:foldl(fun(Upd, Acc) ->
        {ok, NewUpds} = indexing:index_update_hook(Upd, Transaction),
        Acc ++ lists:flatten([NewUpds])
    end, [], [Update] ++ LogUpdates),

    {ok, IndexUpdates}.

generate_log_updates(Key, Type, Bucket, Param, Transaction) ->
    {UpdateOp, Updates} = Param,
    ObjUpdate = ?OBJECT_UPDATE(Key, Type, Bucket, UpdateOp, Updates),

    case update_type({Key, Type, Bucket}) of
        ?RECORD_UPD_TYPE ->
            case Bucket of
                interfaces ->
                    prepare_update(interfaces, ObjUpdate, Transaction);
                ipvfourrib ->
                    prepare_update(ipvfourrib, ObjUpdate, Transaction);
                interfaceneighbour ->
                    prepare_update(interfaceneighbour, ObjUpdate, Transaction);
                _ ->
                    []
            end;
        _ ->
            []
    end.

%% ====================================================================
%% Internal functions
%% ====================================================================

prepare_update(interfaces, ObjUpdate, Transaction) ->
    ?OBJECT_UPDATE(Key, Type, Bucket, _UpdateOp, _Updates) = ObjUpdate,
    %% The bound object variable identifies an object inside
    %% of the database, i.e., it's the key of an object.
    BoundObject = {Key, Type, Bucket},

    %% We are reading the current record from 'interfaces' with
    %% primary key 'Key'
    {OldIp, OldEnabled, OldOperStatus} =
        case table_utils:record_data(BoundObject, Transaction) of
            [] ->
                {undefined, undefined, undefined};
            [OldRecord] ->
                {table_utils:lookup_value(ip, OldRecord),
                    table_utils:lookup_value(enabled, OldRecord),
                    table_utils:lookup_value(operstatus, OldRecord)}
        end,

    %% Now we read the new values introduced by this update
    %% (variable 'ObjUpdate').
    NewIdentifier = Key,
    NewIp = new_column_value(ip, ObjUpdate, OldIp),
    NewEnabled = new_column_value(enabled, ObjUpdate, OldEnabled),
    NewOperStatus = new_column_value(operstatus, ObjUpdate, OldOperStatus),

    LogTable = interfaceschangeslog,
    IpUpdate = interfaceslog_column_update(LogTable, ip, OldIp, NewIp, NewIdentifier, Transaction),
    EnabledUpdate = interfaceslog_column_update(LogTable, enabled, OldEnabled, NewEnabled, NewIdentifier, Transaction),
    OperStatusUpdate = interfaceslog_column_update(LogTable, operstatus, OldOperStatus, NewOperStatus, NewIdentifier, Transaction),

    lists:flatten([IpUpdate, EnabledUpdate, OperStatusUpdate]);

prepare_update(ipvfourrib, ObjUpdate, Transaction) ->
    ?OBJECT_UPDATE(Key, Type, Bucket, _UpdateOp, _Updates) = ObjUpdate,
    BoundObject = {Key, Type, Bucket},

    {OldRoutePrefix, OldPrefixLen, OldSwitchIdFk, ActualNumCols} =
        case table_utils:record_data(BoundObject, Transaction) of
            [] ->
                {undefined, undefined, "", 0};
            [OldRecord] ->
                {table_utils:lookup_value(routeprefix, OldRecord),
                    table_utils:lookup_value(prefixlen, OldRecord),
                    table_utils:lookup_value(switchidentifierfk, OldRecord),
                    length(OldRecord)}
        end,

    NewIdentifier = Key,
    NewRoutePrefix = new_column_value(routeprefix, ObjUpdate, OldRoutePrefix),
    NewPrefixLen = new_column_value(prefixlen, ObjUpdate, OldPrefixLen),
    NewState = new_column_value(?STATE_COL, ObjUpdate, undefined),

    UpdNumCols = count_columns(ObjUpdate),

    NewOperation = new_operation(NewState, UpdNumCols, ActualNumCols),
    NewSwitchIdentifierFk = case NewOperation of
                                delete -> OldSwitchIdFk;
                                _ -> ""
                            end,

    LogTable = ipvfourribchangeslog,
    Update = ipvfourrib_column_update(LogTable, NewIdentifier, NewRoutePrefix,
        NewPrefixLen, NewOperation, NewSwitchIdentifierFk, Transaction),

    Update;

prepare_update(interfaceneighbour, ObjUpdate, Transaction) ->
    ?OBJECT_UPDATE(Key, _Type, _Bucket, _UpdateOp, _Updates) = ObjUpdate,

    NewInterfaceId = Key,

    LogTable = interfaceneighbourchangeslog,
    Update = interfaceneighbourlog_column_update(LogTable, NewInterfaceId, Transaction),
    Update.

%% The two functions below update each one a log table.
%% Each one creates all necessary operations to insert
%% a new record on the respective table and transforms
%% those operations into a single database update.
interfaceslog_column_update(_TableName, _ColName, undefined, _NewVal, _NewIdetifier, _Transaction) ->
    [];
interfaceslog_column_update(_TableName, _ColName, ColVal, ColVal, _NewIdentifier, _Transaction) ->
    [];
interfaceslog_column_update(TableName, ColName, _OldVal, _NewVal, NewIdentifier, Transaction) ->
    GenId = generate_pk(TableName, Transaction),

    Columns = interfaceslog_columns(),
    AllColNames = proplists:get_value(?COLUMNS, Columns),
    ValuesToInsert = [GenId, NewIdentifier, ColName],

    StateOp = {{?STATE_COL, ?STATE_COL_DT}, table_utils:to_insert_op(?CRDT_VARCHAR, 'i')},

    AllOps = [StateOp] ++ insert_data(AllColNames, ValuesToInsert, Columns, []),

    [{{GenId, TableName}, ?TABLE_DT, {update, AllOps}}].

ipvfourrib_column_update(TableName, NewIdentifier, NewRoutePrefix, NewPrefixLen,
    NewOperation, NewSwitchIdentifierFK, Transaction) ->

    GenId = generate_pk(TableName, Transaction),

    Columns = ipvfourriblog_columns(),
    AllColNames = proplists:get_value(?COLUMNS, Columns),

    ValuesToInsert = [GenId, NewIdentifier, NewRoutePrefix, NewPrefixLen, NewOperation, NewSwitchIdentifierFK],

    StateOp = {{?STATE_COL, ?STATE_COL_DT}, table_utils:to_insert_op(?CRDT_VARCHAR, 'i')},

    AllOps = [StateOp] ++ insert_data(AllColNames, ValuesToInsert, Columns, []),

    [{{GenId, TableName}, ?TABLE_DT, {update, AllOps}}].

interfaceneighbourlog_column_update(TableName, NewInterfaceId, Transaction) ->
    GenId = generate_pk(TableName, Transaction),

    Columns = interfaceneighbourlog_columns(),
    AllColNames = proplists:get_value(?COLUMNS, Columns),
    ValuesToInsert = [GenId, NewInterfaceId],

    StateOp = {{?STATE_COL, ?STATE_COL_DT}, table_utils:to_insert_op(?CRDT_VARCHAR, 'i')},

    AllOps = [StateOp] ++ insert_data(AllColNames, ValuesToInsert, Columns, []),

    [{{GenId, TableName}, ?TABLE_DT, {update, AllOps}}].

%% ====================================================================
%% Log table columns specifications
%% ====================================================================

%% Column specifications for the log table 'interfaceschangeslog'
interfaceslog_columns() ->
    IdSpec = {id, ?AQL_INTEGER, primary},
    InterfaceIdSpec = {interfaceidentifier, ?AQL_VARCHAR, ignore},
    UpdateTypeSpec = {updatetype, ?AQL_VARCHAR, ignore},

    Columns = [{id, IdSpec}, {interfaceidentifier, InterfaceIdSpec}, {updatetype, UpdateTypeSpec}],
    Columns ++ [{?PK_COLUMN, [id]}, {?COLUMNS, [id, interfaceidentifier, updatetype]}].

%% Column specifications for the log table 'ipvfourribchangeslog'
ipvfourriblog_columns() ->
    IdSpec = {id, ?AQL_INTEGER, primary},
    IdentifierSpec = {identifier, ?AQL_VARCHAR, ignore},
    RoutePrefixSpec = {routeprefix, ?AQL_VARCHAR, ignore},
    PrefixLenSpec = {prefixlen, ?AQL_INTEGER, ignore},
    OperationSpec = {operation, ?AQL_VARCHAR, ignore},
    SwitchIdentifierSpec = {switchidentifierfk, ?AQL_VARCHAR, {default,""}},

    Columns = [{id, IdSpec}, {identifier, IdentifierSpec}, {routeprefix, RoutePrefixSpec},
        {prefixlen, PrefixLenSpec}, {operation, OperationSpec}, {switchidentifierfk, SwitchIdentifierSpec}],
    Columns ++ [{?PK_COLUMN, [id]}, {?COLUMNS, [id, identifier, routeprefix, prefixlen, operation, switchidentifierfk]}].

%% Column specifications for the log table 'interfaceneighbourchangeslog'
interfaceneighbourlog_columns() ->
    IdSpec = {id, ?AQL_INTEGER, primary},
    InterfaceIdSpec = {interfaceidentifier, ?AQL_VARCHAR, ignore},

    Columns = [{id, IdSpec}, {interfaceidentifier, InterfaceIdSpec}],
    Columns ++ [{?PK_COLUMN, [id]}, {?COLUMNS, [id, interfaceidentifier]}].

%% ====================================================================
%% Log table functions
%% ====================================================================

%% Registers a log table on tables metadata, in case it doesn't exist.
%% Received the table name and a list of predefined columns that
%% will represent the table schema.
create_log_table(TableName, Columns, Transaction) ->
    case table_utils:table_metadata(TableName, Transaction) of
        [] ->
            TableUpdate = create_table_update(TableName, Columns),

            case antidote_hooks:has_hook(pre_commit, TableName) of
                true -> ok;
                false -> antidote_hooks:register_pre_hook(TableName, indexing, index_update_hook)
            end,

            MetadataKey = {?TABLE_METADATA_KEY, ?TABLE_METADATA_DT, ?AQL_METADATA_BUCKET},

            [{MetadataKey, update, [TableUpdate]}];
        _Else ->
            []
    end.

%% Creating an update for the log table, given a table name
%% and a list of columns.
create_table_update(TableName, Columns) ->
    MapEntryKey = {TableName, ?TABLE_NAME_DT},
    TPolicy = {add, undefined, undefined},
    TCols = build_columns(Columns),

    Table = ?TABLE(TableName, TPolicy, TCols, [], []),
    {MapEntryKey, {assign, Table}}.

build_columns(Cols) ->
    build_columns(Cols, maps:new()).

build_columns([{ColName, ColSpec} | Cols], MapAcc) ->
    NewMap = maps:put(ColName, ColSpec, MapAcc),
    build_columns(Cols, NewMap);
build_columns([], MapAcc) ->
    MapAcc.

%% The primary key for the log table is generated automatically,
%% through a counter CRDT that increments monotonically.
generate_pk(TableName, Transaction) ->
    CounterKey = {querying_utils:to_atom(TableName), ?TABLE_DT, ?COUNTER_TABLE},
    {ok, _} = increment_counter(CounterKey),
    Count = read_counter(CounterKey, Transaction),
    querying_utils:to_atom(Count).

increment_counter(CounterKey) ->
    IncrementOp = table_utils:to_insert_op(?CRDT_COUNTER_INT, 1),
    CountUpd = {{'Count',antidote_crdt_counter_pn}, IncrementOp},

    Update = querying_utils:create_crdt_update(CounterKey, update, CountUpd),
    Res = querying_utils:write_keys([Update]),
    Res.

read_counter(CounterKey, _Transaction) ->
    [CounterRecord] = querying_utils:read_keys(value, CounterKey),
    case CounterRecord of
        [] ->
            0;
        _Else ->
            table_utils:lookup_value('Count', CounterRecord)
    end.

%% ====================================================================
%% Auxiliary functions
%% ====================================================================

update_type({?TABLE_METADATA_KEY, ?TABLE_METADATA_DT, ?AQL_METADATA_BUCKET}) -> ?TABLE_UPD_TYPE;
update_type({_Key, ?TABLE_METADATA_DT, ?AQL_METADATA_BUCKET}) -> ?METADATA_UPD_TYPE;
update_type({_Key, ?TABLE_DT, _Bucket}) -> ?RECORD_UPD_TYPE;
update_type(_) -> ?OTHER_UPD_TYPE.

register_trigger(Table, TriggerName) ->
    antidote_hooks:register_pre_hook(Table, ?MODULE, TriggerName).

insert_data([ColName | Columns], [Val | Values], ColumnSpecs, Acc) ->
    {ColName, ColAQLType, _ColConstraint} = proplists:get_value(ColName, ColumnSpecs),
    ColCRDT = table_utils:type_to_crdt(ColAQLType, ignore),
    ColOp = {{ColName, ColCRDT}, table_utils:to_insert_op(ColCRDT, Val)},
    NewAcc = lists:append(Acc, [ColOp]),
    insert_data(Columns, Values, ColumnSpecs, NewAcc);
insert_data([], [], _ColumnSpecs, Acc) ->
    Acc.

%% Function that searches a certain column from an update.
new_column_value(ColName, ObjUpdate, Default) ->
    ?OBJECT_UPDATE(_, _, _, _, Updates) = ObjUpdate,
    Aux = lists:dropwhile(fun(Operation) ->
        ?MAP_OP(Col, _, _, _) = Operation,
        Col /= ColName
                          end, Updates),
    case Aux of
        [] -> Default;
        [Col | _] ->
            ?MAP_OP(_, _, _, Val) = Col,
            Val
    end.

count_columns(?OBJECT_UPDATE(_, _, _, _, Updates)) ->
    length(Updates).

new_operation('i', _, 0) ->
    insert;
new_operation('i', UpdNumCols, ActualNumCols)
    when UpdNumCols < ActualNumCols
    orelse UpdNumCols == ActualNumCols ->
    update;
new_operation('t', _, _) ->
    update;
new_operation('d', _, _) ->
    delete;
new_operation(_, _, _) ->
    undefined.
