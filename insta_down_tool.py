import requests
import json
import requests
import urllib.request
import os
from dotenv import load_dotenv
load_dotenv()

i = 0  # For naming photos downloaded purpose.
path = "./InstaDown/" #Change directory saving pics here

query_hash_for_user = os.getenv("QUERY_HASH_FOR_USER") or "9dcf6e1a98bc7f6e92953d5a61027b98" # Case 1
query_hash_for_specific_post = os.getenv("QUERY_HASH_FOR_POST") or "a92f76e852576a71d3d7cef4c033a95e"  # case 2:

headers = {'cookie': os.getenv("COOKIES") or "sessionid=5711537494%3AsqShow1gFBehyH%3A22;",
'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}

def get_specific_post(shortCode):
    global i, path

    query_hash_url = "https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22shortcode%22%3A%22{}%22%7D".format(
        query_hash_for_specific_post, shortCode)

    # Now we use get method to request and load what we got into json_data
    try:
        response = requests.get(query_hash_url, headers=headers)
        json_data = json.loads(response.text)

        try:
            # Case 1: Post has more than one photo/video
            if json_data['data']['shortcode_media']['__typename'] == 'GraphSidecar':
                print('Downloading file with InstaDown...')
                # Get all nodes of the post.
                for item in json_data['data']['shortcode_media']['edge_sidecar_to_children']['edges']:
                    if item['node']['__typename'] == "GraphImage":  # Only down load image.
                        namePic = '{}instadown_picture_number_{}.jpg'.format(path,i)
                        display_url = item['node']['display_url']
                        urllib.request.urlretrieve(display_url, namePic)
                        i = i + 1

            # Case 2: Post has only one photo/video            
            elif json_data['data']['shortcode_media']['__typename'] == 'GraphImage':
                print('Downloading file #{} with InstaDown...'.format(i))
                namePic = '{}instadown_picture_number_{}.jpg'.format(path, i)
                display_url = json_data['data']['shortcode_media']['display_url']
                urllib.request.urlretrieve(display_url, namePic)
                i = i + 1

            else: print("No image found!")
            print("Completed.")

        except KeyError:
            print(query_hash_url)
            print(json_data)
    except json.decoder.JSONDecodeError:
        print("Can not get photos from that user. Maybe that user doesn't exist.")
    except requests.exceptions.MissingSchema:
        print("Make sure your URL is correct.")
        print("Ex: https://www.instagram.com/p/B8wydAGnk8O/")
    except KeyboardInterrupt:
        print("Downloading canceled. {} photos downloaded.".format(i))
    except Exception as err:
        print("Unhandled exception :(")
        print("Error:", err)
    


def get_all_post_of_user():
    global i, path

    default_first = 50

    print("Enter user's URL profile or username: ")
    input_url_or_username = input()

    if("https://www.instagram.com/" not in input_url_or_username): #username entered
        input_url_or_username = "https://www.instagram.com/"+input_url_or_username+"/"
    url_step1 = input_url_or_username + "?__a=1" if input_url_or_username[len(input_url_or_username)-1] == '/' else input_url_or_username + "/?__a=1"

    try:
        json_data_step1 = requests.get(url_step1, headers=headers).json()
        id_user = json_data_step1['graphql']['user']['id']

        end_cursor = ""
        while (end_cursor != None):
            url_step2 = "https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A{}%2C%22after%22%3A%22{}%22%7D".format(
                query_hash_for_user, id_user, default_first, end_cursor)
            json_data_step2 = requests.get(url_step2, headers=headers).json()

            for item in json_data_step2['data']['user']['edge_owner_to_timeline_media']['edges']:
                if item['node']['__typename'] == 'GraphImage': # One photo/video in this post
                    # print(item['node']['display_url'])
                    print('Downloading file #{} with InstaDown...'.format(i))
                    namePic = '{}instadown_picture_number_{}.jpg'.format(path, i)
                    display_url = item['node']['display_url']
                    urllib.request.urlretrieve(display_url, namePic)
                    i = i + 1
                elif item['node']['__typename'] == 'GraphSidecar': #More than one photo/video in this post
                    for node_item in item['node']['edge_sidecar_to_children']['edges']:
                        if node_item['node']['__typename'] == 'GraphImage':
                            print('Downloading file #{} with InstaDown...'.format(i))
                            display_url1 = node_item['node']['display_url']
                            namePic = '{}instadown_picture_number_{}.jpg'.format(path, i)
                            urllib.request.urlretrieve(display_url1, namePic)
                            i = i + 1
            end_cursor = json_data_step2['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            if end_cursor is not None:
                # Remove the last = in the end_cursor
                end_cursor = end_cursor.replace("=", "")
                # Append  == at last by url encode
                end_cursor += '%3D%3D'  
        print("Completed.")
    except json.decoder.JSONDecodeError:
        print("Can not get photos from that user. Maybe that user doesn't exist.")
    except requests.exceptions.MissingSchema:
        print("Make sure your URL is correct.")
        print("Ex: https://www.instagram.com/taylorswift/")
    except KeyboardInterrupt:
        print("Downloading canceled. {} photos downloaded.".format(i))
    except Exception as err:
        print("Unhandled exception :(")
        print("Error:", err)

def main():
    # Create a directory to store data.
    global path
    os.makedirs("{}".format(path), exist_ok=True)

    print("Download photos from all user's posts or from a specific post? (1 or 2): ")
    choiceType = input()

    if choiceType == '1':
        get_all_post_of_user()

    if choiceType == '2':
        print("Enter the post's URL: ")
        inputUrl = input()

        # Sample url a post Insta: https://www.instagram.com/p/B8wydAGnk8O/
        shortCode = inputUrl.split('/')[4]
        get_specific_post(shortCode)


# main()

if __name__ == "__main__":
    main()
