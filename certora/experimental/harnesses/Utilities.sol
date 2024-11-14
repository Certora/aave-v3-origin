
import {MathUtils} from '../munged/src/contracts/protocol/libraries/math/MathUtils.sol';
import {FlashLoanLogic} from '../munged/src/contracts/protocol/libraries/logic/FlashLoanLogic.sol';
import {DataTypes} from '../munged/src/contracts/protocol/libraries/types/DataTypes.sol';


contract Utilities {
    function havocAll() external {
        (bool success, ) = address(0xdeadbeef).call(abi.encodeWithSelector(0x12345678));
        require(success);
    }

    function justRevert() external {
        revert();
    }

    function nop() external {}

    function SECONDS_PER_YEAR() external view returns (uint256) {
      return MathUtils.SECONDS_PER_YEAR;
    }    
}
