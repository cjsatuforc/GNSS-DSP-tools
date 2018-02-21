# Examples of acquisition and tracking

DATA=data/gnss-20170427-L1L2L5.pcap
DEST_DIR=gnss-20170427-L1L2L5


# GPS L1

#prn   2 doppler  -800.0 metric  3.96 code_offset   43.2
#prn   5 doppler  3000.0 metric  5.19 code_offset  414.1
#prn   6 doppler -3400.0 metric  4.14 code_offset  712.1
#prn   7 doppler   800.0 metric  6.55 code_offset  987.0
#prn   9 doppler -2200.0 metric  7.88 code_offset  650.1
#prn  13 doppler  3400.0 metric  2.68 code_offset  396.4
#prn  23 doppler -3000.0 metric  2.46 code_offset  808.2
#prn  26 doppler -2200.0 metric  2.40 code_offset  299.5
#prn  29 doppler -1200.0 metric  3.89 code_offset  966.3
#prn  30 doppler  3000.0 metric  7.71 code_offset  369.1

al1:
	python ./acquire-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 1

al1f:
	python ./acquire-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000

tg9:
	python ./track-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 9 -2200.0 650.1

tg9e:
	python ./track-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 9 -2200.0 111

tg9f:
	python ./track-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 9 -2200.0 650.1 1

tg30:
	python ./track-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 30 3000.0 369.1

#prn   2 doppler -1600.0 metric  3.21 code_offset    7.0
#prn   4 doppler  3000.0 metric  4.28 code_offset  366.9
#prn   5 doppler -1400.0 metric  5.43 code_offset  969.3
#prn  18 doppler  4200.0 metric  2.55 code_offset  424.6
#prn  21 doppler  2400.0 metric  5.80 code_offset  817.5
#prn  25 doppler -2000.0 metric  2.69 code_offset  969.6
#prn  26 doppler  3400.0 metric  2.95 code_offset  446.3
#prn 135 doppler   800.0 metric  2.90 code_offset 1004.5

al1x:
	python ./acquire-gps-l1.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s8.dat 69984000 -9334875

tg21x:
	python ./track-gps-l1.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s8.dat 69984000 -9334875 21 2400.0 817.5

#prn   5 doppler     0.0 metric  5.29 code_offset 1005.3
#prn  30 doppler -1400.0 metric  3.81 code_offset 1008.8

al1x2:
	python ./acquire-gps-l1.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 

tg5x2:
	python ./track-gps-l1.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 5 0.0 1005.3

tg30x2:
	python ./track-gps-l1.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 30 -1400.0 1008.8


# Galileo E1B

#prn   7 doppler -2450.0 metric  3.21 code_offset 3490.1
#prn  11 doppler  1100.0 metric  2.69 code_offset 1850.6
#prn  12 doppler -1400.0 metric  3.75 code_offset 2212.2
#prn  19 doppler  1700.0 metric  4.67 code_offset 2116.9
#prn  20 doppler  -500.0 metric  3.63 code_offset  939.2
#prn  30 doppler -1250.0 metric  5.57 code_offset    2.6

ae1:
	python ./acquire-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000

ae1f:
	python ./acquire-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 1

t12:
	python ./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 12 -1400.0 2212.2

t19:
	python ./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 19 1700.0 2116.9

t20:
	python ./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 20 -500.0 939.2

t30:
	python ./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 30 -1250.0 2.6

t30f:
	python ./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 30 -1250.0 2.6 1

t30e:
	python ./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 30 -1250.0 999

#prn   7 doppler  -800.0 metric  2.94 code_offset  565.2
#prn  12 doppler  2200.0 metric  3.86 code_offset 2477.2
#prn  14 doppler  3200.0 metric  6.92 code_offset 3770.7
#prn  20 doppler  1600.0 metric  2.82 code_offset 2884.6
#prn  24 doppler   250.0 metric  7.81 code_offset 2838.0
#prn  26 doppler -1000.0 metric  4.97 code_offset 1001.0

ae1x:
	python ./acquire-galileo-e1b.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s8.dat 69984000 -9334875

t3x:
	python ./track-galileo-e1b.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s8.dat 69984000 -9334875 24 250.0 2838.0

#prn   3 doppler   700.0 metric  14.93 code_offset 3072.1

ae1x2:
	python ./acquire-galileo-e1b.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 

t3x2:
	python ./track-galileo-e1b.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 3 700.0 3072.1 1


all: acquire track

acquire: ${DATA}
	mkdir -p ${DEST_DIR}
	acquire-all.sh ${DATA} ${DEST_DIR}

track: ${DATA}
	mkdir -p ${DEST_DIR}
	track-all-gnss-2017-0427-L1L2L5.sh ${DATA} ${DEST_DIR}

# Download the sky-recording waveform

${DATA}:
	mkdir -p data
	wget -O ${DATA} https://rf-waveforms.s3.amazonaws.com/gnss-20170427-L1L2L5.pcap
