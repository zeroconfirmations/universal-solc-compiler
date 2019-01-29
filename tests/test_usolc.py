####################################################################################################
#                                                                                                  #
# (c) 2019 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.      #
#                                                                                                  #
####################################################################################################


from usolc.usolc import *
import pytest


@pytest.fixture
def sample_version_list():
    return ["0.3.9", "0.4.1", "0.4.2", "0.4.3", "0.4.18", "0.5.0", "1.0.0", "1.0.1"]


@pytest.mark.parametrize("rule_text,expected_result", [
    ("^0.4.2", ["0.4.2", "0.4.3", "0.4.18"]),
])
def test_semver_filter(sample_version_list, rule_text, expected_result):
    """ Test semver_filter """
    result = list(semver_filter(sample_version_list, rule_text))
    assert(result == expected_result)


@pytest.mark.parametrize("filename,expected_line",[
    ("exactly_one.sol","pragma solidity 0.4.18;\n"),
    ("caret_0.4.sol","pragma solidity ^0.4.18;\n"),
    ("range.sol","pragma solidity >=0.4.22 <0.6.0;\n"),
    ("range_or_one.sol","pragma solidity 0.4.21 || >=0.4.25 <0.6.0;\n"),
])
def test_extract_pragma_line(filename,expected_line):
    """ Test extract_pragma_line for cases that there both the file and the pragma line exist """
    extracted_line = extract_pragma_line("resources/"+filename)
    assert(expected_line == extracted_line) 


def test_extract_pragma_line_throws_pragmanotfound():
    """
    Test extract_pragma_line throws PragmaLineNotFoundError
    when the file exists but the line doesn't
    """
    with pytest.raises(PragmaLineNotFoundError):
        extract_pragma_line("resources/empty.sol")


def test_extract_pragma_line_throws_file_not_found():
    """ Test extract_pragma_line throws exception FileNotFoundError when the file doesn't exist """
    with pytest.raises(FileNotFoundError):
        extract_pragma_line("from_somerandomfilenamethat_shouldnt_exist.sol")


@pytest.mark.parametrize("pragma, expected_rule",[
    ("pragma solidity 0.4.18;\n", "0.4.18"),
    ("pragma solidity ^0.4.18;\n","^0.4.18"),
    ("pragma solidity >=0.4.22 <0.6.0;\n",">=0.4.22 <0.6.0"),
    ("pragma solidity 0.4.21 || >=0.4.25 <0.6.0;\n","0.4.21 || >=0.4.25 <0.6.0"),       
])
def test_getrule_from_pragma(pragma, expected_rule):
    """ Test getrule_from_pragma """
    extracted_rule = getrule_from_pragma(pragma)
    assert(expected_rule == extracted_rule) 


@pytest.mark.parametrize("filename,expected_rule",[
    ("resources/exactly_one.sol","0.4.18"),
    ("resources/caret_0.4.sol","^0.4.18"),
    ("resources/range.sol",">=0.4.22 <0.6.0"),
    ("resources/range_or_one.sol","0.4.21 || >=0.4.25 <0.6.0"),       
])
def test_getrule_from_file(filename,expected_rule):
    """ Test getrule_from_fiole """
    extracted_rule = getrule_from_file(filename)
    assert(expected_rule == extracted_rule) 


@pytest.mark.parametrize("sys_argv, expected_result",[
    (["solc","hello.sol", "-U", "0.4.2+" , "--abi", "hello"],
     ["hello.sol", ["0.4.2", VersionChoosing.NEWEST], ["hello.sol","--abi", "hello"]]),

    (["solc","hello.sol", "-U", "0.4.2+" , "--abi"],
     ["hello.sol", ["0.4.2", VersionChoosing.NEWEST],["hello.sol","--abi"]]),

    (["solc","hello.sol", "--abi"],
     ["hello.sol", ["*",VersionChoosing.NEWEST], ["hello.sol","--abi"]]),

    (["solc","hello.sol"],
     ["hello.sol", ["*",VersionChoosing.NEWEST], ["hello.sol"]]),
])
def test_extract_arguments(sys_argv, expected_result):
    """ Test extract_arguments when .sol is found in the parameters"""
    extracted_result = extract_arguments(sys_argv)
    assert(expected_result == extracted_result)   


@pytest.mark.parametrize("strategy_string, expected_result",[
    ("^0.4.1+", ["^0.4.1", VersionChoosing.NEWEST]),
    (">=0.4.1 <0.4.23", [">=0.4.1 <0.4.23", VersionChoosing.NEWEST]),
    (">=0.4.1 <0.4.23+", [">=0.4.1 <0.4.23", VersionChoosing.NEWEST]),
    (">=0.4.1 <0.4.23-", [">=0.4.1 <0.4.23", VersionChoosing.OLDEST]),
    (">=0.4.5 <0.4.23 || 0.4.3-", [">=0.4.5 <0.4.23 || 0.4.3", VersionChoosing.OLDEST]),
])
def test_interpret_strategy_string(strategy_string, expected_result):
    """ Test interpret_strategy_string """
    extracted_result = interpret_strategy_string(strategy_string)
    assert(extracted_result == expected_result)


@pytest.mark.parametrize("version_list, expected_version", [
    (["0.3.9", "0.4.1", "0.4.2", "0.4.3", "0.4.18", "0.5.0", "1.0.0", "1.0.1"], "0.3.9"),
    (["1.0.1","0.4.1", "0.3.9", "0.4.2", "0.4.3", "0.4.18", "0.5.0", "1.0.0"],  "0.3.9"),
])
def test_semver_min_satisfying_normal(version_list, expected_version):
    """ Test semver_min_satisfying when there should be a result_version """
    result_version = semver_min_satisfying(version_list, "*")
    assert(result_version == expected_version)


def test_semver_min_satisfying_none(sample_version_list):
    """ Test semver_min_satisfying when result_version should be None """
    result_version = semver_min_satisfying(sample_version_list, ">5.0.0")
    assert(result_version is None)


@pytest.mark.parametrize("version_selection_strategy, expected_version", [
    (["^0.4.1", VersionChoosing.NEWEST],"0.4.18"),
    (["^0.4.1", VersionChoosing.OLDEST], "0.4.1"),
])
def test_choose_version_by_strategy(sample_version_list,
                                    version_selection_strategy, expected_version):
    """ Test choose_version_by_strategy """
    result_version = choose_version_by_strategy(sample_version_list, version_selection_strategy)
    assert(result_version == expected_version)


@pytest.mark.parametrize("filename, version_selection_strategy, expected_version", [
    ("exactly_one.sol", ["^0.4.1", VersionChoosing.NEWEST], "0.4.18"),
    ("caret_0.4.sol", ["0.4.18", VersionChoosing.NEWEST], "0.4.18"),
    ("range.sol", ["*", VersionChoosing.NEWEST], "0.5.0"),
    ("range_or_one.sol",["*", VersionChoosing.NEWEST], "0.5.0"),
])
def test_choose_version_by_argument_normal(sample_version_list,
                                           filename, version_selection_strategy, expected_version):
    """ Test choose_version_by_argument when all arguments are properly given """
    filelocation = "resources/" + filename
    result_version = \
        choose_version_by_argument(sample_version_list, filelocation, version_selection_strategy)
    assert(expected_version == result_version)


def test_choose_version_by_argument_throws_no_version_available_by_sol():
    """
    Test choose_version_by_argument
    when rule from solidity ruled out all available solutions,
    it should throw NoVersionAvailableBySol
    """
    with pytest.raises(NoVersionAvailableBySol):
        choose_version_by_argument(["0.3.9"], "resources/exactly_one.sol", ["*", VersionChoosing.NEWEST])


def test_choose_version_by_argument_throws_no_version_available_by_user():
    """
    Test choose_version_by_argument when rule from solidity
    when rule specified by the user ruled out all available solutions,
    it should throw NoVersionAvailableByUser
    """
    with pytest.raises(NoVersionAvailableByUser):
        choose_version_by_argument(["0.4.18"],
                                   "resources/exactly_one.sol", ["^0.4.19", VersionChoosing.NEWEST])


def test_read_version_list():
    """
    Test read_version_list to see if it properly reads the versions provided in the file,
    The versions should not include special characters like \n or \r
    """
    extracted_list = read_version_list("usolc/solc_version_list")
    expected_list = ["0.5.3", "0.5.2", "0.5.1", "0.5.0", "0.4.25", "0.4.24", "0.4.23", "0.4.22",
                     "0.4.21", "0.4.20", "0.4.19", "0.4.18", "0.4.17"]
    assert(expected_list == extracted_list)


def test_run_solc():
    """
    Test run_solc, passing normal arguments to see if it properly runs without failure
    """
    version_chosen = "0.4.25"
    native_argv = ["resources/caret_0.4.sol", "--abi"]
    process_return = run_solc(version_chosen, native_argv)
    assert(process_return.returncode == 0)


@pytest.mark.parametrize("sys_argv, expected_bin_file",[
    (["solc", "resources/caret_0.4.sol", "--bin", "-o", "test_bin", "-U", "0.4.25"],
     "resources/caret_0.4.25.bin"),
    (["solc", "resources/caret_0.5.sol", "--bin", "-o", "test_bin", "-U", "0.5.0"],
     "resources/caret_0.4.25.bin"),
])
def test_main(sys_argv, expected_bin_file):
    """
    Test main and compile a solidity file for 0.4.25 and another for 0.5.0, compare them with
    the bin file we expected.
    """
    sys.argv = sys_argv
    assert(main() == 0)
    expected_bin_file = [elem.rstrip('\n') for elem in list(open(expected_bin_file, "r"))]
    produced_bin_file = list(open("test_bin/Ballot.bin", "r"))
    assert(expected_bin_file == produced_bin_file)



@pytest.mark.parametrize("sys_argv",[
    (["solc", "resources/empty.sol", "--bin", "-o", "test_bin", "-U", "0.4.25"]),
    (["solc", "some_random_file_should_not_exist.sol", "--bin", "-o", "test_bin", "-U", "0.5.0"]),
    (["solc", "resources/exactly_0.6.0.sol", "--bin", "-o", "test_bin"]),
    (["solc", "resources/caret_0.5.sol", "--bin", "-o", "test_bin", "-U", "0.4.25"]),
])
def test_main_exception_return_1(sys_argv):
    """
    Test if main returns 1 when there is an exception being raised.
    The test cases is going through all exceptions that is being listed in the main()
    """
    sys.argv = sys_argv
    assert(main() == 1)
