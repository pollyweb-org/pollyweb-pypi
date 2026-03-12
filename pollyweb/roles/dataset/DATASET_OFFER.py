from PW_AWS.ITEM import ITEM
from pollyweb import LOG
from pollyweb import STRUCT


class DATASET_OFFER(ITEM):


    def Verify(self):
        self.RequireLocation()
        self.RequireArguments()


    def RequireLocation(self):
        return self.RequireStr('Location')
    
    def GetDefault(self):
        return self.GetStr('Default')

    def RequireArguments(self):
        return self.ListStr('Arguments', require=True)
    

    def PopulateLocation(self, received:STRUCT):
        '''👉 Uses the received arguments to populate the mask placeholders.'''

        STRUCT.AssertClass(received, require=True)

        mask = self.RequireLocation()
        args = self.RequireArguments()

        for arg in args:
            placeholder = '{'+arg+'}'

            # Check if the placeholder was defined on the mask.
            if placeholder not in mask: continue
                
            value = received.RequireStr(arg)
            mask = mask.replace(placeholder, value)

        return mask
