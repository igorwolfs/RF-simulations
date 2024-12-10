# Power meter
We use the AD8317, buyable from amazon for a very very good price.
- Datasheet can be found: https://www.analog.com/media/en/technical-documentation/data-sheets/AD8317.pdf

Can be bought for example with an SMA output at Vout:
- https://www.amazon.com/1M-10GHz-Converter-Logarithmic-Controller-Amplifier/dp/B07RR86PFC/ref=sr_1_4?crid=2DIRRQ2DDWI3K&dib=eyJ2IjoiMSJ9.NCxBxG27fAsnB3jlNgUtWEJXbMNxAJBcfrWlMvVK2e5I4mjBn-H0NNFU0jwuFmPlOGzUhzElr6gDwTYiIiy3nZ_HhCesKIkqdWSLahyVSQzZLIc5u6o4h8QXrjlv2_Tk2D1ZuvLXx8J-XGhcfSCcr4riAaKEUgBOdHao2NdOPETnQ3IeVnYaBP0634nRJA0TEqGPR5pwWFV5C6aYMe15hfUbO788ym8fVxXrBRQEaDc.tdaQpi3jSfkVpwy9doyM958tUGOe22jTqPxToRC1Tb4&dib_tag=se&keywords=AD8317&qid=1733789028&sprefix=%2Caps%2C461&sr=8-4

Or with simply a copper plated surface as output:
- https://www.amazon.com/AD8317-Logarithmic-Detector-1M-10000MHz-Controller/dp/B0C4MBJRTK/ref=sr_1_2?crid=2DIRRQ2DDWI3K&dib=eyJ2IjoiMSJ9.NCxBxG27fAsnB3jlNgUtWEJXbMNxAJBcfrWlMvVK2e5I4mjBn-H0NNFU0jwuFmPlOGzUhzElr6gDwTYiIiy3nZ_HhCesKIkqdWSLahyVSQzZLIc5u6o4h8QXrjlv2_Tk2D1ZuvLXx8J-XGhcfSCcr4riAaKEUgBOdHao2NdOPETnQ3IeVnYaBP0634nRJA0TEqGPR5pwWFV5C6aYMe15hfUbO788ym8fVxXrBRQEaDc.tdaQpi3jSfkVpwy9doyM958tUGOe22jTqPxToRC1Tb4&dib_tag=se&keywords=AD8317&qid=1733789028&sprefix=%2Caps%2C461&sr=8-2

-> Read through it first before ordering it however.
A log here talks about subsampling and averaging: https://pa0rwe.nl/?page_id=356 so it might be good to know how it actually works before buying it.
It might also be a good idea to figure out a way to use an MCU with it before programming it.

# Attenuator
An attenuator will probably also be required when using the power meter, since it's range is
- only between -60 dBm and 0 dBm. So whatever goes over that it can unfortunately not measure.

OR: we could build one ourselves by ordering copper clad's, a soldering iron and some resistors.
https://www.amazon.com/copper-clad-pcb/s?k=copper+clad+pcb

# USB-port safety circuitry
Make sure to buy some safety circuitry for your USB port in case some overcurrent or overvoltage happens on the chip through the power source

Just buy some galvanic isolation usb ports such as this one: https://www.amazon.de/Isolator-Industrielle-Isolatoren-Geschwindigkeit-ADUM4160-Wie-gezeigt/dp/B0BQW71LPP/ref=asc_df_B0BQW71LPP?mcid=10b6da14b403313ba34c978b1566ad04&th=1&psc=1&tag=googshopde-21&linkCode=df0&hvadid=696459872814&hvpos=&hvnetw=g&hvrand=6023424831527551914&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9043142&hvtargid=pla-2323732968444&psc=1&gad_source=1

# Oscilloscope RF probes
Make sure to buy some 50 ohm oscilloscope RF probes + maybe some "high"-voltage probing stuff so you can go up to 50 volts without being scared about it.
