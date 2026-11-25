#!/bin/bash
# Renders a storyboard with two planted mistakes and checks the render is refused
# with both mistakes listed. Run from the renderer folder.
#   - the highlighted planet (venus) isn't one of the planets shown
#   - a number is typed straight into the text
output=$(npx remotion still src/index.ts Reel out/should-not-exist.png --props=tests/bad_storyboard.json "$@" 2>&1)
status=$?

if [ $status -eq 0 ]; then
  echo "FAIL: the bad storyboard was rendered"
  exit 1
fi
for expected in 'must also be in "planets"' 'number typed directly'; do
  if ! grep -q "$expected" <<< "$output"; then
    echo "FAIL: expected the error: $expected"
    echo "$output" | tail -20
    exit 1
  fi
done
echo "OK: the bad storyboard was refused with both mistakes listed"
