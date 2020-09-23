#!/bin/bash -e

test_conf=/opt/test
test_repo=/opt/MultiQC_TestData
# just look at one module, since some sample data fails and we are only testing megaqc
test_data="$test_repo/data/modules/picard"

which git || apk add git
which curl || apk add curl
[[ -d "$test_repo" ]] || git clone https://github.com/ewels/MultiQC_TestData.git "$test_repo"

run_multiqc() {
    multiqc -c "$1" -fo /tmp/upload_test $test_data
}

echo "Testing sending data via proxy"
run_multiqc "$test_conf/proxy_config.yaml"
echo

echo "Testing sending data directly"
run_multiqc "$test_conf/direct_config.yaml"
echo