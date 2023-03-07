#!/usr/bin/env bash
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
	# note that '.' does not work in place of 'source' in zsh for some reason
	echo "[ERROR] you must source env.sh or use dot slash for path"
# note that we nest all conditionals because exit in a sourced script
#   causes you to leave a screen
else
	if [ "$SHELL" = "/bin/zsh" ]; then 
		# via https://stackoverflow.com/a/3572105
		realpath() {
	    	[[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
		}
		DIR=$(dirname $(realpath "$0"))
	else
		# standard bash method
		DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
	fi
	source $DIR/venv/bin/activate
fi
