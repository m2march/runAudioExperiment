% Initializing PsychPortAudio
PsychDefaultSetup(1);
InitializePsychSound;

% Checking device number from console parameters
% if nargin > 0
%     DEVICE_ID = str2num(argv(){1});
% else
%     DEVICE_ID = -1;
% end
% 
% if DEVICE_ID == -1
%     x = disp('No device ID specified.');
%     x = disp('Execute as: octave playrec.m DEVICE_ID');
%     x = disp('');
%     x = disp('Available devices are:');
% 
%     devices = PsychPortAudio('GetDevices');
%     for d = devices
%         x = disp(fprintf('\t%2i : %s\n', d.DeviceIndex, d.DeviceName));
%     end
%     exit()
% end

DEVICE_ID = 3;

% Defining input wavfile to play
in_wavfilename = 'ejemplo_pulso_1.wav';

% Defining output wavfile to store recording
out_wavfilename = 'out.rec.wav';

% Opening file to play
[y, freq] = psychwavread(in_wavfilename);
wavedata = y';
nrchannels = size(wavedata,1); % Number of rows == number of channels.

% Calculating playback length used for recording (with an extra 2 seconds
% to avoid buffer overflow)
playback_length = size(wavedata, 2) / freq;

% Open device for full duplex, allows playback while recording
pahandle = PsychPortAudio('Open', DEVICE_ID, 3, 0, freq, 2);

% Filling the playback buffer with the audio file data
PsychPortAudio('FillBuffer', pahandle, wavedata);

% Create recording buffer equal to the playback length
% (The buffer is 2 seconds longer than playback to avoid buffer overflows)
PsychPortAudio('GetAudioData', pahandle, playback_length + 2); 

% Start playback (one repetition) and recording (because of device mode)
PsychPortAudio('Start', pahandle, 1, 0); % Start asap and wait for start

% Playback and recording stop
PsychPortAudio('Stop', pahandle, 1, 1);

% Obtaining recorded data
audiodata = PsychPortAudio('GetAudioData', pahandle);

% Closing audio device
PsychPortAudio('Close', pahandle);

% Writing audio data to output file
psychwavwrite(transpose(audiodata), freq, 16, out_wavfilename);
