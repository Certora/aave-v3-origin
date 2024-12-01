CMN="--compilation_steps_only"



#echo "******** Running:  1 ***************"
#certoraRun $CMN certora/solvency/confs/solvency/time_passing.conf \
#           --msg "1: time_passing.conf"

echo "******** Running:  2 ***************"
certoraRun $CMN certora/solvency/confs/solvency/borrow.conf \
           --msg "2: borrow.conf"

echo "******** Running:  3 ***************"
certoraRun $CMN certora/solvency/confs/solvency/supply.conf \
           --msg "3: supply.conf"

echo "******** Running:  4 ***************"
certoraRun $CMN certora/solvency/confs/solvency/withdraw.conf \
           --msg "4: withdraw.conf"

echo "******** Running:  5a ***************"
certoraRun $CMN certora/solvency/confs/solvency/repay-indexSUMM.conf \
           --msg "5a: repay-indexSUMM.conf"

echo "******** Running:  5b ***************"
certoraRun $CMN certora/solvency/confs/solvency/repay-NONindexSUMM.conf \
           --msg "5b: repay-NONindexSUMM.conf"

echo "******** Running:  6a ***************"
certoraRun $CMN certora/solvency/confs/solvency/repayWithATokens-HOOKS.conf \
           --multi_assert_check \
           --msg "6a: repayWithATokens-HOOKS.conf"

echo "******** Running:  6b ***************"
certoraRun $CMN certora/solvency/confs/solvency/repayWithATokens-noHOOKS.conf \
           --msg "6b: repayWithATokens-noHOOKS.conf"

echo "******** Running:  7 ***************"
certoraRun $CMN certora/solvency/confs/solvency/flashloan.conf --rule solvency__flashLoanSimple \
           --multi_assert_check \
           --msg "7: flashloan.conf"

echo "******** Running:  8 ***************"
certoraRun $CMN certora/solvency/confs/solvency/cumulateToLiquidityIndexCVL-check.conf --rule check_cumulateToLiquidityIndexCVL \
           --msg "8: cumulateToLiquidityIndexCVL-check.conf ::  check_cumulateToLiquidityIndexCVL"


echo "******** Running:  9a ***************"
certoraRun $CMN certora/solvency/confs/solvency/liquidationCall-DBTasset-main.conf \
           --msg "9a: liquidationCall-DBTasset-main.conf"

echo "******** Running:  9b ***************"
certoraRun $CMN certora/solvency/confs/solvency/liquidationCall-DBTasset-lemma.conf \
           --msg "9b: liquidationCall-DBTasset-lemma.conf"

echo "******** Running:  9c ***************"
certoraRun $CMN certora/solvency/confs/solvency/liquidationCall-DBTasset-totSUP0.conf \
           --msg "9c: liquidationCall-DBTasset-totSUP0.conf"

echo "******** Running:  9d ***************"
certoraRun $CMN certora/solvency/confs/solvency/liquidationCall-COLasset-main.conf \
           --msg "9d: liquidationCall-COLasset-main.conf"

echo "******** Running:  9e ***************"
certoraRun $CMN certora/solvency/confs/solvency/liquidationCall-COLasset-lemma.conf \
           --msg "9e: liquidationCall-COLasset-lemma.conf"

echo "******** Running:  9f ***************"
certoraRun $CMN certora/solvency/confs/solvency/liquidationCall-COLasset-totSUP0.conf \
           --msg "9f: liquidationCall-COLasset-totSUP0.conf"

echo "******** Running:  9g ***************"
certoraRun $CMN certora/solvency/confs/solvency/liquidationCall-COLasset-totSUP0-lemma.conf \
           --msg "9g: liquidationCall-COLasset-totSUP0.conf"





