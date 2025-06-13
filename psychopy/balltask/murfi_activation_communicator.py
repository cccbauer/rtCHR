"""Class to retrieve and store ROI activations from MURFI.
Simulates fake data if `fake=True`.
"""

import socket
import re
import random
import time

class MurfiActivationCommunicator:
    def __init__(self, ip, port, num_trs, roi_names, exp_tr, fake):
        self._ip = ip
        self._port = port
        self._num_trs = num_trs
        self._exp_tr = exp_tr
        self._fake = fake
        self._rois_fake = roi_names
        self._rois = {}
        self._last_update_time_global = time.time()

        for roi_name in roi_names:
            self._rois[roi_name] = {
                'last_tr': -1,
                'activation': [float('NaN')] * self._num_trs
            }

        self._roi_query = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<info>'
            '<get dataid=":*:*:*:__TR__:*:*:roi-weightedave:__ROI__:"></get>'
            '</info>\n'
        )

    def _send(self, mesg):
        if not self._fake:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self._ip, self._port))
            sock.sendall(mesg.encode('utf-8'))
            resp = sock.recv(4096)
            sock.close()
            return resp
        else:
            print("::::DEBUG MODE.RUNNING MURFI SIMULATOR::::")
            for roi_name in self._rois_fake:
                self._rois[roi_name] = str(random.gauss(0, 1))
                resp = self._rois[roi_name].encode()
                print("Simulated:", roi_name, resp)
                return resp

    def _ask_for_roi_activation(self, roi_name, tr):
        if tr >= self._num_trs:
            raise ValueError("Requested TR out of bounds")

        to_send = self._roi_query.replace('__TR__', str(tr + 1)).replace('__ROI__', roi_name)
        resp = self._send(to_send)

        first_re = "<.*?>".encode()
        stripped = re.sub(first_re, b"", resp)

        try:
            num = float(stripped)
        except ValueError:
            num = float('nan')

        return num

    def get_roi_activation(self, roi_name, tr=None):
        if roi_name not in self._rois:
            raise ValueError("No such ROI %s" % roi_name)

        if tr is None:
            tr = self._rois[roi_name]['last_tr']

        if tr < 0 or tr >= self._num_trs:
            raise ValueError("Requested TR out of bounds (tr=%s)" % tr)

        return self._rois[roi_name]['activation'][tr]

    def update(self):
        if not self._fake:
            for roi_name, roi in self._rois.items():
                if roi['last_tr'] >= self._num_trs:
                    continue

                act = self._ask_for_roi_activation(roi_name, roi['last_tr'] + 1)
                while act == act:  # check for non-NaN
                    roi['last_tr'] += 1
                    roi['activation'][roi['last_tr']] = act
                    act = self._ask_for_roi_activation(roi_name, roi['last_tr'] + 1)
        else:
            current_time = time.time()
            if current_time - self._last_update_time_global < self._exp_tr:
                for roi_name, roi in self._rois.items():
                    if roi['last_tr'] < self._num_trs - 1:
                        roi['activation'][roi['last_tr'] + 1] = float('nan')
                return
            else:
                self._last_update_time_global = current_time
                print("::::DEBUG MODE.RUNNING MURFI SIMULATOR::::")
                for roi_name, roi in self._rois.items():
                    if roi['last_tr'] < self._num_trs:
                        simulated_value = random.gauss(0, 1)
                        roi['last_tr'] += 1
                        roi['activation'][roi['last_tr']] = simulated_value
                        print(f"ROI: {roi_name}, TR: {roi['last_tr']}, Activation: {simulated_value}")
