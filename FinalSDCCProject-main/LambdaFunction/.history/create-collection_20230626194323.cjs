const AWS = require('aws-sdk');
const rekognition = new AWS.Rekognition();
exports.handler = async (event) => {
    
    let response = {
        "data": "",
        "message": "",
        "error": ""
    };
    
    
    try {
        
        var params = {
            
            "CollectionId": "mycollection"
        };
         
        const data = await rekognition.createCollection(params).promise();
        
        response.data = data;
        response.message = "Collection Created Successfully";
        response.error = null;
    } catch (e) {
        response.data = null;
        response.message = "Collection Created Failed";
        response.error = e;
    }
    return response;
};