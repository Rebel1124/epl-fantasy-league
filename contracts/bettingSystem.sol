pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract BetAccount is ERC721Full {
    constructor() public ERC721Full("BettingAccountToken", "Account") {}

    struct bettingAccount {
        string name;
        string account;
        uint256 appraisalValue;
    }

    mapping(uint256 => bettingAccount) public betAcc;

    event Appraisal(uint256 tokenId, uint256 appraisalValue);

    function registerBettingAccount(
        address owner,
        string memory name,
        string memory account,
        uint256 initialAppraisalValue
    ) public returns (uint256) {
        uint256 tokenId = totalSupply();

        _mint(owner, tokenId);

        betAcc[tokenId] = bettingAccount(name, account, initialAppraisalValue);

        return tokenId;
    }

    function newAppraisal(
        uint256 tokenId,
        uint256 newAppraisalValue
    ) public returns (uint256) {
        betAcc[tokenId].appraisalValue = newAppraisalValue;

        emit Appraisal(tokenId, newAppraisalValue);

        return betAcc[tokenId].appraisalValue;
    }
}

