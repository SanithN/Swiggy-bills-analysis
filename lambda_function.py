import base64
#from apiclient import errors
import os
import boto3
from botocore.exceptions import ClientError
# from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client import client, tools, file


def get_credentials():
    client_id = os.environ['GMAIL_CLIENT_ID']
    client_secret = os.environ['GMAIL_CLIENT_SECRET']
    refresh_token = os.environ['GMAIL_REFRESH_TOKEN']
    credentials = client.GoogleCredentials(None, 
    client_id, 
    client_secret,
    refresh_token,
    None,
    "https://accounts.google.com/o/oauth2/token",
    'my-user-agent')

    return credentials



def search_email(service, query_string, label_ids=[]):
    try:
        message_list_response = service.users().messages().list(
            userId= 'me',
            labelIds = label_ids,
            q=query_string
        ).execute()
        
        message_items = message_list_response.get('messages')
        nextPageToken = message_list_response.get('nextPageToken')
        
        while nextPageToken:
            message_list_response = service.users().messages().list(
                userId= 'me',
                labelIds = label_ids,
                q=query_string,
                pageToken=nextPageToken
            ).execute()
            message_items.extend(message_list_response.get('messages'))
            nextPageToken = message_list_response.get('nextPageToken')
        return message_items
    
    
    except Exception as e:
        return None


def get_message_detail(service, message_id, format='metadata', metadata_headers=[]):
    try:
        message_detail = service.users().messages().get(
            userId= 'me',
            id= message_id,
            format= format,
            metadataHeaders= metadata_headers
            ).execute()
        return message_detail
        
    except Exception as e:
        print(e)
        return None


def upload_to_aws(local_file, s3_file):
    
    print('Inside upload_to_aws function')

    s3 = boto3.client('s3', aws_access_key_id=os.environ['ACCESS_KEY'], 
                      aws_secret_access_key=os.environ['SECRET_ACCESS_KEY'])
    print('executed boto3')
    try:
        # response = s3.upload_file(local_file, os.environ['BUCKET_NAME'], s3_file)
        file_path = "Raw_data_files/" + s3_file
        print("file_path is", file_path)
        # with open(file_path, 'rb') as data:
        response = s3.put_object(Body=local_file, Bucket=os.environ['BUCKET_NAME'], Key=file_path)
        # url = s3.generate_presigned_url(
        #     ClientMethod='get_object',
        #     Params={
        #         'Bucket': os.environ['BUCKET_NAME'],
        #         'Key': s3_file
        #    
        #     ExpiresIn=24 * 3600
        # )

        # return url
    except ClientError as e:
        logging.error(e)
        return False
    return response
    # except NoCredentialsError:
    #     print("Credentials not available")
    #     return None
    


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
# If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


#####################################################################################    
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#########################################################################################
    try:
#         print(creds)
        # Call the Gmail API
        credentials1 = get_credentials()
#         http = credentials.authorize(httplib2.Http())
#         service = discovery.build('gmail', 'v1', http=http)
        service = build('gmail', 'v1', credentials=credentials1)
        
#         results = service.users().labels().list(userId='me').execute()
#         labels = results.get('labels', [])

#         if not labels:
#             print('No labels found.')
#             return
#         print('Labels:')
#         for label in labels:
#             print(label['name'])
        query_string = 'has:attachment from:noreply@swiggy.in'
        email_messages = search_email(service, query_string, ['INBOX'])
#         print(email_messages)
        count = 0
# tobewritten        folder_name = 'Email_Attachments'
# tobewritten        parent_dir = os.path.abspath(os.curdir)
# tobewritten        save_path = create_folder(folder_name, parent_dir)
        for email_message in email_messages:
            count = count+1
            messageId = email_message['threadId']
            messageSubject = '(No Subject) ({0})'.format(messageId)
            messageDetail = get_message_detail(service, email_message['id'], format='full', metadata_headers=['parts'])
            messageDetailPayload = messageDetail.get('payload')
#             messageDetailPayload['headers']
#            print(messageDetailPayload)
       
        
        

            if 'parts' in messageDetailPayload:
                for msgPayload in messageDetailPayload['parts']:
                    mime_type = msgPayload['mimeType']
                    file_name = msgPayload['filename'][5:]
                    # file_name = "Raw_data_files/" + file_name_1
                    print(file_name)
                    body = msgPayload['body']

                    if 'attachmentId' in body:
                        attachment_id = body['attachmentId']

                        response = service.users().messages().attachments().get(
                            userId='me',
                            messageId=email_message['id'],
                            id=attachment_id).execute()
                        file_data = base64.urlsafe_b64decode(
                            response.get('data').encode('UTF-8'))
        #                     name_of_file = xxxxx
                        # print(file_data)

# tobewritten                        updated_path = os.path.join(save_path, file_name) 

# tobewritten                       curpath = os.path.abspath(os.curdir)
        #                     print ("Current path is: %s" % (curpath))
        #                     print ("Trying to open: %s" % (os.path.join(curpath, file_name)))
                        
                        File_save_location = upload_to_aws(file_data, file_name)
                        res = File_save_location.get('ResponseMetadata')
                        if res.get('HTTPStatusCode') == 200:
                            print('File Uploaded Succesfully')
                        else:
                            print('Not uploaded')
#    tobewritten                     with open(updated_path, 'wb') as f:
#    tobewritten                         f.write(file_data)
                        

        print(count)  
    except Exception as e:
        print(e)
        # TODO(developer) - Handle errors from gmail API.
        # print(f'An error occurred: {error}')


# if __name__ == '__main__':
#     main()
    

def lambda_handler(event, context):
    main()