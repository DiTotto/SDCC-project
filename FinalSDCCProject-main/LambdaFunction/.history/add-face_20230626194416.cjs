const AWS = require('aws-sdk');
const rekognition = new AWS.Rekognition();
exports.handler = async (event) => {
    
    let response = {
        "data": "",
        "message": "",
        "error": ""
    };
    
    
    try {
        
        const encodedImage = event.imgdata;
        const decodedImage = Buffer.from(encodedImage, 'base64');

        let params = {
            CollectionId: "mycollection", 
            DetectionAttributes: [
                "DEFAULT"
            ], 
            ExternalImageId: "Nicola", 
            Image: {
                Bytes: decodedImage
            }
        };
        
        const data = await rekognition.indexFaces(params).promise();
        
        response.data = data;
        response.message = "Face Added Successfully!!"
        response.error = null;
    } catch (e) {
        response.data = null;
        response.message = "Failed to Add Face Data!!"
        response.error = e;
    }
    return response;
};