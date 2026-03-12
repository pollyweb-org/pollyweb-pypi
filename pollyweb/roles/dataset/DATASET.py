from DATASET_OFFERS import DATASET_OFFERS
from PW_DOMAIN import CODE
from PW import PW
from MSG import MSG
from pollyweb import STRUCT
from pollyweb import UTILS


class DATASET:

    
    @classmethod
    def OFFERS(cls):
        return DATASET_OFFERS()


    @classmethod
    def InvokeQuery(cls, supplier:str, input:dict, output:str):
        UTILS.RequireArgs([supplier, output, input])
        
        CODE.Verify(output)

        answer = PW.BEHAVIORS().SYNCAPI().Invoke(
            to= supplier, 
            subject= 'Query@Dataset',
            body= {
                'Dataset': output,
                'Arguments': input
            })
        
        return answer.RequireStructs('Dataset')


    @classmethod
    def HandleQuery(cls, event):

        # Parse the request.
        msg = MSG(event)
        msg.MatchSubject('Query@Dataset')
        args = msg.RequireStruct('Arguments')
        code = msg.RequireStr('Dataset')
        CODE.Verify(code)

        # Read the offer from the database.
        offer = cls.OFFERS().RequireOffer(code)

        # Replace the argment placeholders to get the path.
        path = offer.PopulateLocation(args)

        # Read the YAML file from S3.
        text = PW.AWS().S3().GetText(path)

        # Convert from YAML into an object.
        yaml = UTILS.FromYaml(text)

        return yaml