// The DOT language grammar as found online on:
//      https://graphviz.gitlab.io/_pages/doc/info/lang.html


// Discard Comments and whitespace
COMMENT_PRE: /^#[^\n]*/
COMMENT_SNG: "//" /[^\n]/*
COMMENT_MLT: /\/\*[^*]*\*+(?:[^\/*][^*]*\*+)*\//

%ignore WS
%ignore COMMENT_PRE
%ignore COMMENT_SNG
%ignore COMMENT_MLT

start: graph
graph: STRICT? (GRAPH|DIGRAPH) id? "{" stmt_list "}"
stmt_list: (stmt ";"? stmt_list)?
stmt: node_stmt | edge_stmt | attr_stmt | (id "=" id) | subgraph
attr_stmt: (GRAPH | NODE | EDGE) attr_list
attr_list: "[" a_list? "]" attr_list?
a_list: id "=" id (";" | ",")? a_list?
edge_stmt: (node_id | subgraph) edge_rhs attr_list?
edge_rhs: edgeop (node_id | subgraph) edge_rhs?
edgeop: DIOP | UNOP
node_stmt: node_id attr_list?
node_id: id port?
port: (":" id (":" compass_pt)?) | (":" compass_pt)
subgraph: ("subgraph" id?)? "{" stmt_list "}"
compass_pt: "n" | "ne" | "e" | "se" | "s" | "sw" | "w" | "nw" | "c" | "_"

// Operators
DIOP: "->"
UNOP: "--"

// case-independant keywords
NODE: "node"i
EDGE: "edge"i
GRAPH: "graph"i
DIGRAPH: "digraph"i
SUBGRAPH: "subgraph"i
STRICT: "strict"i

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMERAL: /[-]?(.[0-9]+|[0-9]+(.[0-9]*)?)/
STRING: "\"" /[^\"\\]*(?:\\.[^\"\\]*)*/ "\""
HTML: /<.*?>/
id: NAME | NUMERAL | STRING | HTML

%import common.WS
