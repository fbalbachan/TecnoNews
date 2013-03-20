#!/bin/bash
source ./freeling_config/server
source ./freeling_config/port
# $FREELING_SERVER 5555 -f ./freeling_config/v2.2.2/es.cfg --utf --outf parsed
#$FREELING_SERVER $FREELING_PORT -f ./freeling_config/v3-alpha/es.cfg --outf parsed
$FREELING_SERVER -f es.cfg --outf parsed --server --port $FREELING_PORT
