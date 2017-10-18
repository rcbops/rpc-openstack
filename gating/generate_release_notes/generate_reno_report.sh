#!/bin/bash -x

release=${1}
out_file=${2}
err_file=${out_file}.err
rst_file=${out_file}.rst

reno report --branch ${release} --version ${release} --no-show-source --output ${rst_file} &> ${err_file}
return_code=$?
cat $err_file

if [[ ${return_code} != 0 ]]; then
  if grep -q "KeyError: '${release}'" ${err_file}; then
    cat > ${out_file} << EOF
Release Notes
=============

${release}
-------------

### No release notes

EOF
    return_code=0
    echo "Warning: No new Reno release notes found, this can indicate an issue with the tag."
  else
    echo "Failure: Reno failed to generate the report."
  fi
else
  pandoc --from rst --to markdown_github < ${rst_file} > ${out_file}
  echo "Success: New Reno release notes found."
fi

exit ${return_code}
