#!/bin/bash
echo "[Launcher] Starting CDDA CWM Server..."
./cdda/build/src/cdda-server --socket /tmp/cwm_bench_ipc.sock --world test_world --userdir /tmp/cdda_cwm_bench_user > cdda_server.log 2>&1 &
SERVER_PID=$!

sleep 2
echo "[Launcher] Starting Luanti Presentation Client..."
./luanti/bin/luanti > luanti_client.log 2>&1 &
CLIENT_PID=$!

echo "[Launcher] Both processes started."
echo "CDDA Server PID: $SERVER_PID"
echo "Luanti Client PID: $CLIENT_PID"
echo "To stop them, run: kill $SERVER_PID $CLIENT_PID"

wait $CLIENT_PID
kill $SERVER_PID
