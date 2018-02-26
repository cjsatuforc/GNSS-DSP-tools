# Examples of acquisition and tracking

DATA=data/gnss-20170427-L1L2L5.pcap
DEST_DIR=gnss-20170427-L1L2L5

all: al1x2

####################################################################################################
# GPS L1

#prn   2 doppler  -800.0 code_offset   43.2 metric  3.97 *******************
#prn   5 doppler  3000.0 code_offset  414.1 metric  5.22 **************************
#prn   6 doppler -3400.0 code_offset  712.1 metric  4.17 ********************
#prn   7 doppler   800.0 code_offset  987.0 metric  6.58 ********************************
#prn   9 doppler -2200.0 code_offset  650.1 metric  7.91 ***************************************
#prn  13 doppler  3400.0 code_offset  396.4 metric  2.70 *************
#prn  16 doppler  -800.0 code_offset  928.8 metric  1.93 *********
#prn  23 doppler -3000.0 code_offset  808.2 metric  2.47 ************
#prn  26 doppler -2200.0 code_offset  299.5 metric  2.41 ************
#prn  29 doppler -1200.0 code_offset  966.3 metric  3.91 *******************
#prn  30 doppler  3000.0 code_offset  369.1 metric  7.72 **************************************

al1:
	./acquire-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 cs8 interp
#	./acquire-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 cs8 interp search2

# test saturated values, works but slightly less sensitivity
al1t:
	./acquire-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 cs82

al1f:
	./acquire-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 cs8 SE4150L

tg9:
	./track-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 9 -2200.0 650.1

tg30:
	./track-gps-l1.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 30 3000.0 369.1

# fine search
#prn   2 doppler -1624.0 code_offset    7.0 metric  3.20 ****************
#prn   4 doppler  2996.0 code_offset  366.9 metric  4.27 *********************
#prn   5 doppler -1369.0 code_offset  969.3 metric  5.40 ***************************
#prn  13 doppler  3317.0 code_offset  160.6 metric  1.89 *********
#prn  15 doppler  3874.0 code_offset  786.5 metric  1.45 *******
#prn  18 doppler  4192.0 code_offset  424.6 metric  2.53 ************
#prn  20 doppler  1874.0 code_offset  166.3 metric  1.49 *******
#prn  21 doppler  2430.0 code_offset  817.5 metric  5.81 *****************************
#prn  25 doppler -1922.0 code_offset  969.6 metric  2.71 *************
#prn  26 doppler  3411.0 code_offset  446.3 metric  2.94 **************
#prn  29 doppler  1493.0 code_offset  233.3 metric  1.49 *******
#prn 135 doppler   878.0 code_offset 1004.5 metric  2.92 **************

# NB 2-bit 1,3,-1,-3 data
al1x:
	./acquire-gps-l1.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s82.dat 69984000 -9334875 cs8 interp

tg21x:
	./track-gps-l1.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s82.dat 69984000 -9334875 21 2430.0 817.5

# using "rs8"
#prn   1 doppler  1400.0 code_offset  198.3 metric  5.84 *****************************
#prn   2 doppler -4000.0 code_offset  383.4 metric  1.61 ********
#prn   5 doppler   800.0 code_offset  878.9 metric  3.52 *****************
#prn   6 doppler  2800.0 code_offset   18.2 metric  1.36 ******
#prn  10 doppler -1400.0 code_offset  336.4 metric  1.84 *********
#prn  13 doppler  1000.0 code_offset  840.7 metric  2.11 **********
#prn  16 doppler  2200.0 code_offset  318.9 metric  2.86 **************
#prn  21 doppler  2000.0 code_offset  962.6 metric  4.70 ***********************
#prn  23 doppler  -600.0 code_offset   50.5 metric  2.46 ************
#prn  25 doppler -3600.0 code_offset  435.8 metric  4.00 *******************
#prn  29 doppler -2200.0 code_offset   40.0 metric  6.82 **********************************
#prn  30 doppler -2200.0 code_offset  857.7 metric  7.47 *************************************
#prn  31 doppler -2000.0 code_offset  534.5 metric  5.69 ****************************

al1x2:
	./acquire-gps-l1.py ../samples/primo.fs.5456.if4092.iq.s8.dat 5456000 4092000 rs8

ag30x2:
	./track-gps-l1.py ../samples/primo.fs.5456.if4092.iq.s8.dat 5456000 4092000 30 -2200.0 857.7 rs8

#prn   5 doppler     0.0 metric  5.29 code_offset 1005.3
#prn  30 doppler -1400.0 metric  3.81 code_offset 1008.8

al1x3:
	./acquire-gps-l1.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0

tg5x3:
	./track-gps-l1.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 5 0.0 1005.3

tg30x3:
	./track-gps-l1.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 30 -1400.0 1008.8

#prn   5 doppler -4000.0 metric  4.46 code_offset  330.4
#prn  13 doppler  -400.0 metric  2.54 code_offset  326.2
#prn  15 doppler  1400.0 metric  2.83 code_offset  174.1
#prn  20 doppler -1400.0 metric  2.14 code_offset  859.2
#prn  28 doppler -1000.0 metric  3.44 code_offset  729.8
#prn  30 doppler -3600.0 metric  3.80 code_offset  525.2

al1x4:
	./acquire-gps-l1.py ../samples/RTLSDR_Bands-L1.fs.2.048M.iq.s8.dat 2048000 cs8


####################################################################################################
# Galileo E1B

# fine search
#prn   7 doppler -2427.0 code_offset 3490.1 metric  3.63 ******************
#prn  11 doppler  1112.0 code_offset 1850.6 metric  3.03 ***************
#prn  12 doppler -1385.0 code_offset 2212.2 metric  4.28 *********************
#prn  18 doppler -4100.0 code_offset 1091.2 metric  3.19 ***************
#prn  19 doppler  1686.0 code_offset 2116.9 metric  5.24 **************************
#prn  20 doppler  -515.0 code_offset  939.2 metric  4.13 ********************
#prn  30 doppler -1267.0 code_offset    2.6 metric  6.26 *******************************

ae1:
	./acquire-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000

t30 te1b:
	./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 30 -1267.0 2.6

tup:
	./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 30 -1267.0 2.6 up

t19:
	./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 19 1686.0 2116.9

t12:
	./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 12 -1400.0 2212.2

t20:
	./track-galileo-e1b.py ../samples/HackRF_Bands-L1.fs.10M.if.420k.iq.s8.dat 10000000 420000 20 -500.0 939.2

# NB 2-bit 1,3,-1,-3 data processed as cs8
#prn   7 doppler  -800.0 code_offset  565.2 metric  2.79 *************
#prn  12 doppler  2200.0 code_offset 2477.2 metric  3.79 ******************
#prn  14 doppler  3200.0 code_offset 3770.7 metric  7.03 ***********************************
#prn  20 doppler  1600.0 code_offset 2884.6 metric  2.77 *************
#prn  24 doppler   250.0 code_offset 2838.0 metric  7.45 *************************************
#prn  26 doppler -1000.0 code_offset 1001.0 metric  4.94 ************************

ae1x:
	./acquire-galileo-e1b.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s82.dat 69984000 -9334875 cs8 interp

t24x te1w:
	./track-galileo-e1b.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s82.dat 69984000 -9334875 24 250.0 2838.0 down

t14x:
	./track-galileo-e1b.py ../samples/gnss-20170427-L1.fs.69.984M.if.-9.334875M.iq.s82.dat 69984000 -9334875 14 3200.0 3770.7

# none! pre-Galileo capture?

ae1x2:
	./acquire-galileo-e1b.py ../samples/primo.fs.5456.if4092.iq.s8.dat 5456000 4092000 rs8

t2x2:
	./track-galileo-e1b.py ../samples/primo.fs.5456.if4092.iq.s8.dat 5456000 4092000 2 2222 222.2 rs8

#prn   3 doppler   700.0 code_offset 3072.1 metric  15.00 ***************************************************************************

ae1x3:
	./acquire-galileo-e1b.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 

t3x3:
	./track-galileo-e1b.py ../samples/test_14_cut.fs.50M.iq.s8.dat 50000000 0 3 700.0 3072.1

# NB 2-bit 1,3,-1,-3 data
# nothing found, but unknown what PRNs were being transmitted back then

ae1x4:
	./acquire-galileo-e1b.py ../samples/gioveAB.fs.16367600.if.4130400.iq.s82.bin 16367600 4130400


allOFF: acquire track

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
