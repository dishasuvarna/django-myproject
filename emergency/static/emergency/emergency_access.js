(function () {
    const STATES = {
        IDLE: 'IDLE',
        CHALLENGE: 'CHALLENGE',
        VERIFYING: 'VERIFYING',
        AUTHORIZED: 'AUTHORIZED'
    };

    const TOKEN_TTL_MS = 5 * 60 * 1000;
    const LOCATION_TIMEOUT_MS = 18000;
    const TARGET_ACCURACY_METERS = 25;
    const MAX_ACCEPTABLE_ACCURACY_METERS = 100;
    const h = React.createElement;

    function requestJson(url, options) {
        return fetch(url, options).then(function (response) {
            if (!response.ok) {
                return response.json()
                    .catch(function () {
                        return {};
                    })
                    .then(function (payload) {
                        throw new Error(payload.error || 'Request failed');
                    });
            }

            return response.json();
        });
    }

    function parsePatientId(qrCodeMessage) {
        try {
            const data = JSON.parse(qrCodeMessage);
            return data.patient_id || data.id || '';
        } catch (err) {
            return qrCodeMessage.trim();
        }
    }

    function getAccuratePosition(onProgress) {
        return new Promise(function (resolve, reject) {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported'));
                return;
            }

            let bestPosition = null;
            let settled = false;
            let watchId = null;

            function finish(position) {
                if (settled) return;
                settled = true;

                if (watchId !== null) {
                    navigator.geolocation.clearWatch(watchId);
                }

                clearTimeout(timeoutId);

                if (position) {
                    resolve(position);
                } else {
                    reject(new Error('Unable to get accurate location'));
                }
            }

            const timeoutId = setTimeout(function () {
                if (bestPosition && (bestPosition.coords.accuracy || Infinity) <= MAX_ACCEPTABLE_ACCURACY_METERS) {
                    finish(bestPosition);
                    return;
                }

                finish(null);
            }, LOCATION_TIMEOUT_MS);

            watchId = navigator.geolocation.watchPosition(function (position) {
                const currentAccuracy = position.coords.accuracy || Infinity;
                const bestAccuracy = bestPosition ? bestPosition.coords.accuracy || Infinity : Infinity;

                if (!bestPosition || currentAccuracy < bestAccuracy) {
                    bestPosition = position;

                    if (onProgress) {
                        onProgress({
                            accuracy: currentAccuracy,
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        });
                    }
                }

                if (currentAccuracy <= TARGET_ACCURACY_METERS) {
                    finish(position);
                }
            }, function (err) {
                if (settled) return;
                settled = true;
                navigator.geolocation.clearWatch(watchId);
                clearTimeout(timeoutId);

                if (err && err.code === 1) {
                    reject(new Error('Location permission denied'));
                    return;
                }

                if (err && err.code === 2) {
                    reject(new Error('Location unavailable'));
                    return;
                }

                reject(new Error('Unable to get accurate location'));
            }, {
                enableHighAccuracy: true,
                timeout: LOCATION_TIMEOUT_MS,
                maximumAge: 0
            });
        });
    }

    function EmergencyAccessApp() {
        const config = window.EmergencyAccessConfig || {};
        const [state, setState] = React.useState(STATES.IDLE);
        const [patientId, setPatientId] = React.useState('');
        const [patientData, setPatientData] = React.useState(null);
        const [verifiedLocation, setVerifiedLocation] = React.useState(null);
        const [locationAccuracy, setLocationAccuracy] = React.useState(null);
        const [locationStatus, setLocationStatus] = React.useState('');
        const [scannerStatus, setScannerStatus] = React.useState('Starting camera...');
        const [error, setError] = React.useState('');

        const scannerRef = React.useRef(null);
        const scannedRef = React.useRef(false);
        const tokenRef = React.useRef(null);
        const tokenTimerRef = React.useRef(null);

        React.useEffect(function () {
            startScanner();

            function clearToken() {
                tokenRef.current = null;
            }

            window.addEventListener('beforeunload', clearToken);

            return function () {
                clearToken();
                window.removeEventListener('beforeunload', clearToken);

                if (tokenTimerRef.current) {
                    clearTimeout(tokenTimerRef.current);
                }

                if (scannerRef.current) {
                    scannerRef.current.stop()
                        .then(function () {
                            return scannerRef.current.clear();
                        })
                        .catch(function () {});
                }
            };
        }, []);

        React.useEffect(function () {
            if (state !== STATES.AUTHORIZED || !verifiedLocation) return undefined;

            const map = L.map('authorized-map').setView(
                [verifiedLocation.latitude, verifiedLocation.longitude],
                verifiedLocation.accuracy && verifiedLocation.accuracy > 80 ? 15 : 16
            );

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            L.marker(
                [verifiedLocation.latitude, verifiedLocation.longitude],
                {
                    icon: L.divIcon({
                        className: '',
                        html: '<div class="pulse-marker"></div>',
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                    })
                }
            ).addTo(map);

            if (verifiedLocation.accuracy) {
                L.circle([verifiedLocation.latitude, verifiedLocation.longitude], {
                    radius: verifiedLocation.accuracy,
                    color: '#0b6bcb',
                    weight: 1,
                    fillColor: '#0b6bcb',
                    fillOpacity: 0.12
                }).addTo(map);
            }

            setTimeout(function () {
                map.invalidateSize();
            }, 0);

            return function () {
                map.remove();
            };
        }, [state, verifiedLocation]);

        function startScanner() {
            scannerRef.current = new Html5Qrcode('reader');

            Html5Qrcode.getCameras()
                .then(function (cameras) {
                    if (!cameras.length) {
                        throw new Error('No camera found');
                    }

                    const backCamera = cameras.find(function (camera) {
                        return /back|rear|environment/i.test(camera.label);
                    });
                    const cameraId = backCamera ? backCamera.id : cameras[0].id;

                    return scannerRef.current.start(
                        cameraId,
                        {
                            fps: 12,
                            qrbox: function (viewfinderWidth, viewfinderHeight) {
                                const minEdge = Math.min(viewfinderWidth, viewfinderHeight);
                                const boxSize = Math.floor(minEdge * 0.72);

                                return {
                                    width: boxSize,
                                    height: boxSize
                                };
                            },
                            aspectRatio: 1.333
                        },
                        handleScanSuccess,
                        function () {}
                    );
                })
                .then(function () {
                    setScannerStatus('Align the QR code inside the frame.');
                })
                .catch(function (err) {
                    setScannerStatus('');
                    setError(err.message || 'Unable to start camera');
                });
        }

        function handleScanSuccess(qrCodeMessage) {
            if (scannedRef.current) return;

            const scannedPatientId = parsePatientId(qrCodeMessage);

            if (!scannedPatientId) {
                setError('Invalid QR code');
                return;
            }

            scannedRef.current = true;
            setScannerStatus('QR detected. Checking patient...');

            if (scannerRef.current) {
                scannerRef.current.stop().catch(function () {});
            }

            requestJson(`/api/emergency/${encodeURIComponent(scannedPatientId)}/`)
                .then(function () {
                    setPatientId(scannedPatientId);
                    setError('');
                    setState(STATES.CHALLENGE);
                })
                .catch(function (err) {
                    scannedRef.current = false;
                    startScanner();
                    setError(err.message);
                });
        }

        function verifyLocation() {
            setError('');
            setLocationAccuracy(null);
            setLocationStatus('Finding the best GPS fix...');
            setState(STATES.VERIFYING);

            getAccuratePosition(function (sample) {
                setLocationAccuracy(Math.round(sample.accuracy));
                setLocationStatus(
                    sample.accuracy <= TARGET_ACCURACY_METERS
                        ? 'Strong GPS fix locked.'
                        : 'Refining position...'
                );
            })
                .then(function (position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    const accuracy = Math.round(position.coords.accuracy || 0);

                    return requestJson('/api/verify-location/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': config.csrfToken || ''
                        },
                        body: JSON.stringify({
                            patient_id: patientId,
                            latitude: latitude,
                            longitude: longitude
                        })
                    }).then(function (verification) {
                        tokenRef.current = verification.access_token;

                        tokenTimerRef.current = setTimeout(function () {
                            tokenRef.current = null;
                        }, TOKEN_TTL_MS);

                        return requestJson('/api/emergency-data/', {
                            headers: {
                                Authorization: `Bearer ${tokenRef.current}`
                            }
                        }).then(function (data) {
                            return {
                                data: data,
                                location: {
                                    latitude: latitude,
                                    longitude: longitude,
                                    accuracy: accuracy
                                }
                            };
                        });
                    });
                })
                .then(function (result) {
                    tokenRef.current = null;
                    setLocationStatus('');
                    setVerifiedLocation(result.location);
                    setPatientData(result.data);
                    setState(STATES.AUTHORIZED);
                })
                .catch(function (err) {
                    tokenRef.current = null;
                    setLocationStatus('');
                    setError(
                        err.message === 'Unable to get accurate location'
                            ? 'Location is too coarse. Move outdoors or near a window and retry.'
                            : (err.message || 'Location verification failed')
                    );
                    setState(STATES.CHALLENGE);
                });
        }

        function renderIdle() {
            return h('div', null,
                h('div', { className: 'scanner-card' },
                    h('div', { id: 'reader', className: 'scanner' }),
                    h('div', { className: 'scanner-frame' }),
                    h('p', { className: 'scanner-status' }, scannerStatus)
                )
            );
        }

        function renderChallenge() {
            return h('div', { className: 'panel' },
                h('h3', null, 'Location Required'),
                h('p', null, 'Patient record is locked until location is verified.'),
                h('button', { className: 'button', onClick: verifyLocation }, 'Verify Location')
            );
        }

        function renderVerifying() {
            return h('div', { className: 'panel' },
                h('h3', null, 'Verifying'),
                h('p', null, 'Checking location and secure access...'),
                locationStatus ? h('p', { className: 'location-accuracy' }, locationStatus) : null,
                locationAccuracy ? h('p', { className: 'location-accuracy' }, `Best fix: ${locationAccuracy} meters`) : null
            );
        }

        function renderAuthorized() {
            return h('div', { className: 'panel' },
                h('h3', null, 'Emergency Data'),
                h('p', null, h('b', null, 'Blood Group: '), patientData.blood_group || ''),
                h('p', null, h('b', null, 'Allergies: '), patientData.allergies || ''),
                h('p', null, h('b', null, 'Medications: '), patientData.medications || ''),
                h('p', null, h('b', null, 'Emergency Instructions: '), patientData.emergency_instructions || ''),
                h('p', null, 'Location verified and secure emergency access granted.'),
                verifiedLocation && verifiedLocation.accuracy
                    ? h('p', { className: 'location-accuracy' }, `Location accuracy: ${verifiedLocation.accuracy} meters`)
                    : null,
                h('div', { id: 'authorized-map', className: 'map' })
            );
        }

        function renderState() {
            if (state === STATES.IDLE) return renderIdle();
            if (state === STATES.CHALLENGE) return renderChallenge();
            if (state === STATES.VERIFYING) return h('div', null,
                renderVerifying(),
                locationAccuracy ? h('p', { className: 'location-accuracy' }, `Best location accuracy: ${locationAccuracy} meters`) : null
            );
            if (state === STATES.AUTHORIZED && patientData) return renderAuthorized();
            return null;
        }

        return h('div', { className: 'emergency-shell' },
            renderState(),
            error ? h('p', { className: 'error' }, error) : null
        );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(h(EmergencyAccessApp));
})();
