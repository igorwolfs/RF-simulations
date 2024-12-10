# Goals
## Advanced PCB traces
- Simulate bending PCB traces.
- Simulate PCB trace with via's.

## Antenna design and PCB trace simulations
### Patch antenna

- Figure out why increasing the dielectric height decreases the S-parameter
    - It's not the dielectric loss
    - Maybe the impedance? -> It seems like the impedance is about 216 ohms for the antenna, probe impedance is 1 point and is 50 ohms, let's change that however don't think its the issue.

- Check whether wavelength corresponds to expected resonance frequency for length 
- fix frequency offset for modified grid
- Change patch antenna geometry (adding thickness, changing length for frequency)
- Simulate antenna with feed point, not just patch. 
- Simulate a fed microstrip antenna.

### Trace simulation
- Check the bldc SWD trace simulation that goes through a via.

### Real-life antenna experiments
- Check if you can build a simple patch antenna that can be realistically reproduced in real life.
So
- Check default copper thickness.

**Copper plate + FR4**

Can be both copper and FR4 attached, or separate

Examples:
Link 1: https://www.amazon.de/-/en/sourcing-single-sided-copper-clad-thickness-prototype/dp/B07RL2QJN2/ref=pd_sbs_d_sccl_3_2/259-8279023-2039014?pd_rd_w=R3pzQ&content-id=amzn1.sym.49f459c6-2c34-4c10-b7c3-10d8e862ad07&pf_rd_p=49f459c6-2c34-4c10-b7c3-10d8e862ad07&pf_rd_r=C5ZABDK93TM0Y2CFZJGR&pd_rd_wg=cXw6d&pd_rd_r=bcbdee12-df95-4121-96f5-a512d36a8902&pd_rd_i=B07RL2QJN2&psc=1, thickness 1.5 mm
Link 2: https://www.amazon.de/-/en/sourcing-Single-Copper-Laminate-Universal/dp/B07H3S1FKQ/ref=pd_sbs_d_sccl_3_6/259-8279023-2039014?pd_rd_w=R3pzQ&content-id=amzn1.sym.49f459c6-2c34-4c10-b7c3-10d8e862ad07&pf_rd_p=49f459c6-2c34-4c10-b7c3-10d8e862ad07&pf_rd_r=C5ZABDK93TM0Y2CFZJGR&pd_rd_wg=cXw6d&pd_rd_r=bcbdee12-df95-4121-96f5-a512d36a8902&pd_rd_i=B07H3S1FKQ&th=1, thickness 1.5 mm

**Copper Sheets**

Make sure the copper foil is actually more or less conductive.
Also make sure that if you use tape, the adhesive is in facto conductive and not isolating.

-> prefer tape in this case.

Examples:
- simple foil: https://www.amazon.de/-/en/Copper-Foil-Cut-0-2-Piece/dp/B01G384M7E
- Conductive copper foil tape: https://www.amazon.com/TOP-MAGNETS-2inchX39-4FT-Conductive-Electrical/dp/B0D89QV1NX/ref=sr_1_21?dib=eyJ2IjoiMSJ9.jBY_ljiWSvai35PU27-NGb6xprkDjS_JB3BjQmYMUnl5pNmIdv6bOtP-Hrory9vRF0rn1GxdnIS0mH603X7DGh0nJODVNUbAS9Zwpz_zxaJm5R3np_hKZ7HdKaetUklioV7b_gD8Nl9gBD4HtSMEbb0bQdkSQju1n9eAVePwDWt2OUOUx7eq9TxUXc6KVf948SgXpz99CwHtCTxFBvv-LfQVcWoZNzx-QySRQCzvOZQ.cRniLcH4EJkn1xadpEtOvAN7c7Ik5GY5gdXnrkqsspc&dib_tag=se&keywords=copper%2Bfoil&qid=1733059916&sr=8-21&th=1


**Adhesive**
3M conductive adhesive tape or epoxy adhesives designed for RF applications (like Hysol EA 9361).

**Connectors**
WARNING: SMA vs SMA-RP
-> The SMA connector has a pin sticking out of it, the SMA-RP doesn't, it has a hole instead.

- SMA-connectors work with most signals. (up to 27 GHz)
- N-connectors: work up until the GHz range (more durable + more expensive + higher power rating, usually used by signal analyzers.)
- BNC: usually not used for antennas (mostly for oscilloscopes)
- UHF connectors (PL-259, SO-239), very old, usually low MHz range.

-> CONCLUSION: buy SMA connectors

- The pluto-sdr module has 2 female inputs
- there is 1 male to male SMA adapter cable

So buy 
- 1 male to male SMA adapter
- 2 female to male SMA adapter (so we can have female inputs for the PCB)
- Buy a few male and a few female SMA connectors to be soldered

Examples:
- Link 1: SMA male to female cable https://www.amazon.de/-/en/Superbat-Coaxial-Adapter-Amateur-Antenna-Pack-2/dp/B086JJM654/ref=pd_ci_mcx_pspc_dp_d_2_t_2?pd_rd_w=LvKVe&content-id=amzn1.sym.97f85cc5-92fe-4835-b4c8-321118252f33&pf_rd_p=97f85cc5-92fe-4835-b4c8-321118252f33&pf_rd_r=GZFBYGZ9WBVDM3A7CVBG&pd_rd_wg=3nJPh&pd_rd_r=97aa6687-772a-467d-b925-35c497d04bac&pd_rd_i=B086JH3NKM&th=1
- Link 2: SMA female connectors for soldering https://www.amazon.de/-/en/Connector-Wireless-Devices-Equipments-Transfer/dp/B0C5CRML4K/ref=pd_sbs_d_sccl_3_4/259-8279023-2039014?pd_rd_w=SUJcB&content-id=amzn1.sym.49f459c6-2c34-4c10-b7c3-10d8e862ad07&pf_rd_p=49f459c6-2c34-4c10-b7c3-10d8e862ad07&pf_rd_r=8XWNQFEK1QVVKC7QT9AD&pd_rd_wg=1i4qE&pd_rd_r=7ca434be-093f-444a-bd6e-9af2edac4561&pd_rd_i=B0C5CRML4K&psc=1

**Solder equipment**

### More info on soldering SMA connectors
SMA edge launch connector assembly: https://www.youtube.com/watch?v=lFLgEpMB31M

**USB Galvanic isolation**
To protect laptop from possible overvoltages

### VNA (Vector Network Analyzer)
Buy a vector network analyzer for magnitude and impedance phase measurements.

- Looks like the best one so far:https://eleshop.eu/litevna-5341.html
(Lite VNA)
