// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Append-only pseudonymous research commitments. Never store raw biometrics.
contract SomaticValidation {
    error ZeroCommitment();
    error DuplicateStudy(bytes32 studyId);
    error UnknownStudy(bytes32 studyId);
    error NotResearcher(address caller);
    error TrajectoryAlreadyCommitted(bytes32 studyId, bytes32 subjectKey, uint64 index);

    struct Study { address researcher; bytes32 protocolHash; uint64 registeredAt; }
    struct Commitment { bytes32 baselineHash; bytes32 trajectoryHash; uint64 committedAt; }

    mapping(bytes32 => Study) public studies;
    mapping(bytes32 => Commitment) private commitments;

    event StudyRegistered(bytes32 indexed studyId, address indexed researcher, bytes32 protocolHash);
    event TrajectoryCommitted(bytes32 indexed studyId, bytes32 indexed subjectKey, uint64 indexed trajectoryIndex, bytes32 baselineHash, bytes32 trajectoryHash);

    function registerStudy(bytes32 studyId, bytes32 protocolHash) external {
        if (studyId == bytes32(0) || protocolHash == bytes32(0)) revert ZeroCommitment();
        if (studies[studyId].researcher != address(0)) revert DuplicateStudy(studyId);
        studies[studyId] = Study(msg.sender, protocolHash, uint64(block.timestamp));
        emit StudyRegistered(studyId, msg.sender, protocolHash);
    }

    function commitTrajectory(bytes32 studyId, bytes32 subjectKey, uint64 index, bytes32 baselineHash, bytes32 trajectoryHash) external {
        Study memory study = studies[studyId];
        if (study.researcher == address(0)) revert UnknownStudy(studyId);
        if (msg.sender != study.researcher) revert NotResearcher(msg.sender);
        if (subjectKey == bytes32(0) || baselineHash == bytes32(0) || trajectoryHash == bytes32(0)) revert ZeroCommitment();
        bytes32 key = commitmentKey(studyId, subjectKey, index);
        if (commitments[key].committedAt != 0) revert TrajectoryAlreadyCommitted(studyId, subjectKey, index);
        commitments[key] = Commitment(baselineHash, trajectoryHash, uint64(block.timestamp));
        emit TrajectoryCommitted(studyId, subjectKey, index, baselineHash, trajectoryHash);
    }

    function getCommitment(bytes32 studyId, bytes32 subjectKey, uint64 index) external view returns (Commitment memory) {
        return commitments[commitmentKey(studyId, subjectKey, index)];
    }

    function verify(bytes32 studyId, bytes32 subjectKey, uint64 index, bytes32 baselineHash, bytes32 trajectoryHash) external view returns (bool) {
        Commitment memory item = commitments[commitmentKey(studyId, subjectKey, index)];
        return item.committedAt != 0 && item.baselineHash == baselineHash && item.trajectoryHash == trajectoryHash;
    }

    function commitmentKey(bytes32 studyId, bytes32 subjectKey, uint64 index) public pure returns (bytes32) {
        return keccak256(abi.encode(studyId, subjectKey, index));
    }
}

