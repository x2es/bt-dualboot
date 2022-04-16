#
# NOTE: this module should be sh compatible (not bash)
#

#
# Test launcher
#
# Forwards all command line arguments except own.
# Invokes pytest or ptw, allows jump to container shell before tests
#
# Usage:
#   PROJECT_DIR=$(pwd)
#   . $PROJECT_DIR/tests_integration/helpers.sh
#   pytest_launcher "$@"
#   
#
# @param --watch: start with --ptw
# @param --shell: start bash after tests
#
pytest_launcher() {
  PROJECT_DIR=$(pwd)
  TEST_MODULE_DIR=$(dirname $0)

  fl_shell=0
  fl_watch=0
  fl_print_usage_after=0

  for arg do
    shift
    
    case "$arg" in
      "-h"|"--help")
        set -- "$@" "$arg"
        fl_print_usage_after=1
        ;;

      "--launcher-help")
        pytest_launcher_usage
        exit 0
        ;;

      "--require-virtual-env")
        if [ "$PYTEST_LAUNCHER_VIRTUAL_ENV" != "1" ]; then
          echo "WARNING: My be unsafe to invoke in real environment"
          echo "Define PYTEST_LAUNCHER_VIRTUAL_ENV=1"
          exit 1
        fi
        ;;

      "--tests-dir")
        TEST_MODULE_DIR=$1
        shift
        ;;

      "-w"|"--watch")
        fl_watch=1
        ;;

      "--shell")
        fl_shell=1
        ;;
      *)
        set -- "$@" "$arg"
    esac
    [ $# -eq 0 ] && break
  done

  echo "TIP: use '$0 --launcher-help' for useful opts"

  if [ $fl_watch -eq 1 ]; then
    echo "-w: implies ptw"
    ( set -x ; ptw -- --last-failed --new-first -v $TEST_MODULE_DIR "$@" )
  else
    ( set -x ; pytest $TEST_MODULE_DIR "$@" )
  fi
  [ $fl_print_usage_after -eq 1 ] && echo && pytest_launcher_usage
  [ $fl_shell -eq 1 ] && bash
}


pytest_launcher_usage() {
  TEST_MODULE_DIR="$(dirname $0)/"

  echo "\nusage: $0 [--launcher-help] [--tests-dir DIR] [--require-virtual-env]"
  echo "            [-w|--watch] [--shell] [--pdb] [-x] [...]"
  echo "\nLaunches pytest directly or using ptw (-w) and forwards specified options"
  echo "\nOptions intercepted by launcher:"
  echo "  -h, --help                  show downstream help then this help"
  echo "  --launcher-help             show this help"
  echo "  --require-virtual-env       fails unless PYTEST_LAUNCHER_VIRTUAL_ENV=1 set"
  echo "  --tests-dir                 [default: '$TEST_MODULE_DIR' - launcher dir] path to tests"
  echo "  -w, --watch                 watch on files changes using ptw"
  echo "  --shell                     spawn shell after tests (for Docker context)"
  echo "\nUseful Debug options:"
  echo "  --pdb                       drop to debugger on failure"
  echo "  --pdb -x                    drop to PDB on first failure, then end test session"
  echo "\nOther options:"
  echo "  all options forwared to downstream pytest or ptw invocation"
  echo "\n"
}
