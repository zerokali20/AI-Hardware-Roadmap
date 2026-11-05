
#!/usr/bin/env bash

set -u

TESTS=(
    pc if ifid decode imm regfile ifidstage
    alu aluctrl idex execute branch exbranch
    pipectrl pipeint exmem dmem memstage
    memwb wb wbint forward hazard hazint
    exforward cpu cpuhaz cpuisa cpumembranch cpuperf
)

PASSED=0
FAILED=0

mkdir -p logs

for test in "${TESTS[@]}"; do
    echo "Running $test..."

    make clean > /dev/null 2>&1

    if make TEST="$test" > "logs/${test}.log" 2>&1; then
        echo "PASS: $test"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: $test"
        FAILED=$((FAILED + 1))
        tail -25 "logs/${test}.log"
    fi
done

echo
echo "========== REGRESSION SUMMARY =========="
echo "Passed suites: $PASSED"
echo "Failed suites: $FAILED"
echo "Total suites:  $((PASSED + FAILED))"

if [ "$FAILED" -ne 0 ]; then
    exit 1
fi
