import os
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy
from scipy.special import softmax

def allot(prediction):
    x = prediction.index(max(prediction))
    if x == 0:
        return "negative"
    elif x == 1:
        return "neutral"
    elif x == 2:
        return "positive"
    else:
        return "unknown"

def model_fn(model_dir):
    """
    Load the model for inference
    """
    model_path = os.path.join(model_dir, 'tokenizer/')

    # Load BERT tokenizer from disk.
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Load BERT model from disk.
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    
    model_dict = {'model': model, 'tokenizer':tokenizer}
    return model_dict

def predict_fn(input_data, model):
    """
    Apply model to the incoming request
    """

    tokenizer = model['tokenizer']
    bert_model = model['model']
    

    encoded_input = tokenizer(input_data, truncation = True, max_length = 500, return_tensors='pt')

    result = bert_model(**encoded_input)

    # post processing of the result
    scores = result[0][0].detach().numpy()
    scores_final = softmax(scores)
    scores_final = list(scores_final)
    result = allot(scores_final)
    final = {
        "result": result,
        "scores": scores_final
    }
    return final

def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """

    if request_content_type == "application/json":
        request = json.loads(request_body)

    else:
        request = request_body
        
    return request["inputs"] 

def output_fn(prediction, response_content_type):
    """
    Serialize and prepare the prediction output
    """
    
    #float32 to float conversion
    prediction["scores"] = [float(score) for score in prediction["scores"]]
    
    if response_content_type == "application/json":
        response = json.dumps(prediction)
        
    else:
        response = json.dumps(prediction)

    return response