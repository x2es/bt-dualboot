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
# @param --shell: start bash before tests
#
pytest_launcher() {

  PROJECT_DIR=$(pwd)
  TEST_MODULE_DIR=$(dirname $0)

  fl_shell=0
  fl_watch=0

  for arg do
    shift
    
    case "$arg" in
      "-w"|"--watch")
        fl_watch=1
        ;;

      "--shell")
        fl_shell=1
        ;;
      *)
        set -- "$@" "$arg"
    esac
  done

  [ $fl_shell -eq 1 ] && bash
  if [ $fl_watch -eq 1 ]; then
    ptw -- --last-failed --new-first -v $TEST_MODULE_DIR $@
  else
    pytest $TEST_MODULE_DIR "$@"
  fi
}
