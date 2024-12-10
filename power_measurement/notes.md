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

