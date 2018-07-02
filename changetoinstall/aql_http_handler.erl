-module(aql_http_handler).
-export([handle/2, handle_event/3]).

-include_lib("elli/include/elli.hrl").
-behaviour(elli_handler).

-define(DEFAULT_NODE, list_to_atom(os:getenv("ANTIDOTE_NODENAME2"))).

handle(Req, _Args) ->
    %% Delegate to our handler function
    handle(Req#req.method, elli_request:path(Req), Req).

handle('POST',[<<"aql">>], Req) ->
    case elli_request:post_arg_decoded(<<"query">>, Req, <<"undefined">>) of
        <<"undefined">> ->
            {400, [], <<"No query parameter in POST request body!">>};
        Query ->
            io:format("Received query: ~p~n" , [Query]),
            Node = read_node(Req),
            io:format("Using node: ~p~n", [Node]),
            Result = aqlparser:parse({str, binary_to_list(Query)}, Node),
            case Result of
                {ok, QueryRes, _Tx} ->
                    {ok, [], jsx:encode(QueryRes)};
                {error, Message} ->
                    ErrorMsg = lists:concat(["Error: ", Message]),
                    {500, [], list_to_binary(ErrorMsg)};
                _Else ->
                    {ok, [], jsx:encode(Result)}
            end
    end;

handle(_, _, _Req) ->
    {404, [], <<"Not Found">>}.

%% @doc Handle request events, like request completed, exception
%% thrown, client timeout, etc. Must return `ok'.
handle_event(_Event, _Data, _Args) ->
    ok.

read_node(Req) ->
    case elli_request:post_arg_decoded(<<"node">>, Req, <<"undefined">>) of
        <<"undefined">> -> ?DEFAULT_NODE;
        Node -> list_to_atom(binary_to_list(Node))
    end.