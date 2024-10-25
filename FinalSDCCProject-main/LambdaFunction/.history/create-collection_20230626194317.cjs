const AWS = require('aws-sdk');
const rekognition = new AWS.Rekognition();
exports.handler = async (event) => {
    // Form the response to be returned
    let response = {
        "data": "",
        "message": "",
        "error": ""
    };
    
    // Create a collection
    try {
        // Name the collection uniquely
        var params = {
            //"faces-collection"
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