#!/bin/sh

export HOST_BD=190.101.98.80
export USER_BD=jonnattan
export PASS_BD=wsxzaq123
export AES_KEY="dRgUkXp2s5v8y/B?E(H+MbQeThVmYq3t"
export SLACK_NOTIFICATION=https://hooks.slack.com/services/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
export API_KEY_ROBOT_UPTIME=ur1829961-20881ef84e8d2bcd3d4c98e4

cd /home/opc/server
python Servidor.py 8080
