#CMN="--compilation_steps_only"



#echo "******** Running:  1 ***************"
#certoraRun $CMN certora/experimental/confs/solvency/time_passing.conf \
#           --msg "1: time_passing.conf"

echo "******** Running:  2 ***************"
certoraRun $CMN certora/experimental/confs/solvency/borrow.conf \
           --msg "2: borrow.conf"

echo "******** Running:  3 ***************"
certoraRun $CMN certora/experimental/confs/solvency/supply.conf \
           --msg "3: supply.conf"

echo "******** Running:  4 ***************"
certoraRun $CMN certora/experimental/confs/solvency/withdraw.conf \
           --msg "4: withdraw.conf"

echo "******** Running:  5a ***************"
certoraRun $CMN certora/experimental/confs/solvency/repay-indexSUMM.conf \
           --msg "5a: repay-indexSUMM.conf"

echo "******** Running:  5b ***************"
certoraRun $CMN certora/experimental/confs/solvency/repay-NONindexSUMM.conf \
           --msg "5b: repay-NONindexSUMM.conf"

echo "******** Running:  6a ***************"
certoraRun $CMN certora/experimental/confs/solvency/repayWithATokens-HOOKS.conf \
           --multi_assert_check \
           --msg "6a: repayWithATokens-HOOKS.conf"

echo "******** Running:  6b ***************"
certoraRun $CMN certora/experimental/confs/solvency/repayWithATokens-noHOOKS.conf \
           --msg "6b: repayWithATokens-noHOOKS.conf"

echo "******** Running:  7 ***************"
certoraRun $CMN certora/experimental/confs/solvency/flashloan.conf --rule solvency__flashLoanSimple \
           --multi_assert_check \
           --msg "7: flashloan.conf"

echo "******** Running:  8 ***************"
certoraRun $CMN certora/experimental/confs/solvency/cumulateToLiquidityIndexCVL-check.conf --rule check_cumulateToLiquidityIndexCVL \
           --msg "8: cumulateToLiquidityIndexCVL-check.conf ::  check_cumulateToLiquidityIndexCVL"


#echo "******** Running:  9 ***************"
#certoraRun $CMN certora/experimental/confs/solvency.conf --rule solvency__liquidationCall \
#           --msg "9: solvency.conf ::  liquidationCall"





