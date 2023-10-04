import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import os
from pathlib import Path
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import csv
import json
from PIL import Image
import random
import glob
import photoshop.api as ps
from woocommerce import API
import openai
import time
import pyautogui
import shutil
import pygetwindow as gw
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")


class OperatingSystem:
    def __init__(self) -> None:
        self.user_profile_folder =os.environ['USERPROFILE']
        self.to_upload_to_wp_folder = 'UPLOADED_TO_WP'
        self.desktop_folder = 'OneDrive\\Desktop'
        self.my_documents = 'Documents'
        self.temp_folder = 'C:\\temp\\'


    def activate_window(self, window_name:str):
        windows = gw.getWindowsWithTitle('')
        a = [x for x in windows if window_name in x.title]
        if len(a) > 0:
            try:
                a[0].activate()
            except:
                pass
            a[0].show()
            a[0].restore()
        return



    def get_most_recent_download_file(self):
        dir_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
        files = glob.glob(dir_path + "/*")
        latest_file = max(files, key=os.path.getctime)
        return latest_file
    
    
        
        paths = sorted(Path(dir_path).iterdir())
        filename = [x for x in paths if filename in x.name]

    def get_remote_file(self, url, save_as):
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_as, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded and saved as '{save_as}'.")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    def crop_image(self, image_path:str, percent:int):

        original_image = Image.open(image_path)
        width, height = original_image.size
        new_width = int(width * percent)
        new_height = int(height * percent)
        
        left = (width - new_width) // 2
        upper = (height - new_height) // 2
        right = left + new_width
        lower = upper + new_height
        cropped_image = original_image.crop((left, upper, right, lower))
        
        #cropped_image.show()  # Display the cropped image
        
        # Save the cropped image to a file
        cropped_image.save(image_path)

    def get_list_of_folders(self, parent_folder):
        folders = []
        for item in os.listdir(parent_folder):
            item_path = os.path.join(parent_folder, item)
            if os.path.isdir(item_path):
                folders.append(item_path)
        return folders

    def create_folder(self, folder_name):
        try:
            os.mkdir(folder_name)
            print(f"Folder '{folder_name}' created successfully.")
        except FileExistsError:
            print(f"Folder '{folder_name}' already exists.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def setup_filenames(self, p):
        
        path_and_title = os.path.join(p['destination_path'],p['product_title'])
        file_names = {
            'destination_file_path':path_and_title + p['start_file'],
            'watercolour_mockup':path_and_title +'-'+'0watercolour' + ".jpg",
            'watercolour_macro':path_and_title +'-'+'watercolour-macro' + ".jpg",
            #'local_upscaled_image':path_and_title +'-'+'high-res' + ".jpg",
            #'vectorized_image':path_and_title +'-'+'vector' + ".svg",
            'magnet_filename':path_and_title + 'magnetic.jpg',
            'no_frame_filename':path_and_title + 'no_frame.jpg',
            'black_frame_file':path_and_title + 'black.jpg',
            'white_frame_file':path_and_title + 'white.jpg',
            'oak_frame_file':path_and_title + 'oak.jpg',
            'walnut_frame_file':path_and_title + 'walnut.jpg'
        }
        return file_names

class PlaceItNet:
    def __init__(self) -> None:
        self.base_url = "https://www.placeit.net"
        self.login_status = False
        self.driver = webdriver.Chrome(options=options)
        self.cookies = None
    
    def main_job(self, p):
        print('placeit')
        #favourite_list = self.get_favourites_list()
        templates = [
            {'endpoint':'/c/mockups/stages/mockup-of-a-poster-frame-hanging-next-to-a-floor-lamp-2021-el1'},
            {'endpoint':'/c/mockups/stages/mockup-of-a-squared-art-print-placed-on-a-wooden-wall-m31595'},
            
        ]
        self.upload_file_to_placeit(self.base_url + templates[0]['endpoint'],p['watercolour-mockup'])
        self.crop_image()
        self.download_most_recent_render(p['placeit_image_png'])
        image = Image.open(p['placeit_image_png'])  # Replace 'input.png' with the path to your PNG image
        image.convert('RGB').save(p['placeit_image_jpg'], 'JPEG')
        os.remove(p['placeit_image_png'])

    def crop_image(self):
        # selector = '.zoomInput'
        time.sleep(2)
        # zoomInput = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        # zoomInput.send_keys(Keys.UP, Keys.UP, Keys.UP, Keys.UP, Keys.UP, Keys.UP)   
        selector = '.cropButton'
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector))).click()

    def get_recently_uploaded(self):
        if os.path.exists('recently_uploaded_images.json')== True:
            with open('recently_uploaded_images.json', 'r', newline='') as f:
                f_c = f.read()
                return(json.loads(f_c))
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        url = "https://placeit.net/api/v2/recently_uploaded_images"
        time.sleep(3)
        self.driver.get(url)
        json_data = json.loads(self.driver.find_element(By.CSS_SELECTOR,"body").text)
        # Close the new tab
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return json_data        
    
    def render_template(self, url):
        self.driver.get("https://placeit.net/c/mockups/stages/art-print-mockup-featuring-modern-furniture-2538-el1?customG_0=rwm744f02c")

    def download_template(self):
        download_button = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.download-button.show')))
        download_button.click()
        self.driver.implicitly_wait(10)
        download_to_desktop = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "my-drive-downloads-thumbnail"))).click()
        
    def resize_image(self):
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.drawer-copy')))
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.file-reposition-label'))).click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.reset-cropper'))).click()
        zoomInput = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.zoomInput')))
        zoomInput.send_keys(Keys.UP, Keys.UP, Keys.UP, Keys.UP, Keys.UP, Keys.UP)        
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.cropButton'))).click()
        
    def download_most_recent_render(self, destination_file):
        time.sleep(20)
        download_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.download-container')))
        download_button.click()
        time.sleep(20)
        downloads = self.get_url('https://placeit.net/api/v1/base/processing')
        downloads['items'][-1]['url']
        my_os.get_remote_file(downloads['items'][-1]['url'], destination_file)
        pass
        #machine_download = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.my-drive__breakdown-list li:first-child')))
        #machine_download.click()
    
    def get_template_list(self, templates_url='https://placeit.net/print-on-demand', data_file='pod_templates.json'):
        if os.path.exists(data_file)== True:
            with open(data_file, 'r', newline='') as f:
                f_c = f.read()
                image_attribs = json.loads(f_c)
        else:
            image_attribs = []
            
            for page_number in range(0,26):
                params = {
                    'f_devices':'Art Print',
                    'page':page_number
                }
                
                response = requests.get(templates_url,params = params)
                if response.status_code == 200:
                    # Extract the filename from the URL
                    soup = BeautifulSoup(response.content, "html.parser")
                    li_tags = soup.find_all("li", class_="grid-item")                
                    for li_tag in li_tags:
                        a_tag = li_tag.find_all("a")[0]
                        href=a_tag.get("href")
                        
                        image = li_tag.find_all('img')[1]
                        image_src = image.get("src")
                        image_alt = image.get('alt')
                        
                        image_attribs.append({'href':href,
                                            'image_src':image_src, 
                                            'image_alt':image_alt
                                            })
                    

            with open(data_file, 'w', newline='') as json_file:
                json.dump(image_attribs, json_file)
        return image_attribs

    def get_favourites_list(self, templates_url='https://placeit.net/favorites', data_file='favourites.json'):
        if os.path.exists(data_file)== True:
            with open(data_file, 'r', newline='') as f:
                f_c = f.read()
                image_attribs = json.loads(f_c)
        else:
            image_attribs = []
            response = requests.get(templates_url)
            if response.status_code == 200:
                # Extract the filename from the URL
                soup = BeautifulSoup(response.content, "html.parser")
                li_tags = soup.find_all("li", class_="grid-item")                
                for li_tag in li_tags:
                    a_tag = li_tag.find_all("a")[0]
                    href=a_tag.get("href")
                    
                    image = li_tag.find_all('img')[1]
                    image_src = image.get("src")
                    image_alt = image.get('alt')
                    
                    image_attribs.append({'href':href,
                                        'image_src':image_src, 
                                        'image_alt':image_alt
                                        })
                    

            with open(data_file, 'w', newline='') as json_file:
                json.dump(image_attribs, json_file)
        return image_attribs

    def login_to_place_net(self):
        print('logging in to placeit')
        self.driver.get("https://www.placeit.net")

        try:
            selector = '.modal.back-to-school .modal-dialog .modal-content .modal-body .close'
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector))).click()
        except:
            pass

        login_button = self.driver.find_element(By.ID, 'loginLink').click()

        username_field = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login_user_email")))
        username_field.click()
        username_field.send_keys('jackdtowner@yahoo.co.uk')

        password_field = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login_user_password")))
        password_field.click()
        password_field.send_keys('28Maryrose!!')
        time.sleep(2)
        login_submit = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#login_btn_container'))).click()
        time.sleep(2)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".item.my-placeit")))
        self.login_status = True
        self.cookies = self.driver.get_cookies()
        self.headers = self.driver.execute_script("return Object.assign({}, window.navigator);")
   
    def get_url(self, url:str) -> json:
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(url)
        json_data = json.loads(self.driver.find_element(By.CSS_SELECTOR,"body").text)
        # Close the new tab
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return json_data
        
    def upload_file_to_placeit(self,template_url, file_path):
        # Navigate to the placeit.net website
        time.sleep(5)
        self.driver.get("https://placeit.net/c/mockups/stages/minimal-mockup-featuring-a-square-poster-frame-hanging-by-a-lamp-2020-el1")        
        time.sleep(10)
        selector = '.file-delete-label__title'
        try:
            if WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector))):
                self.driver.find_element(By.CSS_SELECTOR, selector).click()
        except:
            pass    
        #chrome_window = gw.getWindowsWithTitle('Make Mockups, Logos, Videos and Designs in Seconds - Google Chrome')[0]
        #chrome_window.activate()
        selector = '.btn.dropdown-toggle.btn-default'
        self.driver.find_element(By.CSS_SELECTOR, selector).click()
        selector = '.upload-from-device .text'
        self.driver.find_element(By.CSS_SELECTOR, selector).click()
        time.sleep(3)
        pyautogui.write(file_path)
        pyautogui.press('enter')
        return

        # Locate the input element that allows you to choose a file

        # Send the path of the picture file to the input element
        # Replace "image.jpg" with your own file name and location
        #

        # Locate the "Crop Image" button and click it
        #crop_button = self.driver.find_element(By.XPATH, "//button[text()='Crop Image']")
        #crop_button.click()

class PhotoShop:
    def __init__(self):
        self.app = ps.Application()

    def save_as(self, filename, quality=12):
        options = ps.JPEGSaveOptions(quality=quality)
        # # save to jpg
        doc = self.app.activeDocument
        doc.saveAs(filename, options, True )

    def main_job(self, p):
        
        print('photoshop')

        artwork_folder = os.path.join(p['project_folder_stem'],p['project_folder'])

        image_filename_stem = p['product_title']

        l = p['local_filenames']

        #add 0.94 crop action here
        self.open_file_run_action_save_file_close(l['destination_file_path'],'add watercolour texture',l['watercolour_mockup'])
        self.open_file_run_action_save_file_close(l['watercolour_mockup'],'make macro',l['watercolour_macro'])
        self.open_file_run_action_save_file_close(l['watercolour_mockup'], 'magnet', l['magnet_filename'])
        self.open_file_run_action_save_file_close(l['watercolour_mockup'], 'no frame', l['no_frame_filename'])
        self.open_file_run_action_save_file_close(l['watercolour_mockup'], 'black frame', l['black_frame_file'])
        self.open_file_run_action_save_file_close(l['watercolour_mockup'], 'white frame', l['white_frame_file'])
        self.open_file_run_action_save_file_close(l['watercolour_mockup'], 'oak frame', l['oak_frame_file'])
        self.open_file_run_action_save_file_close(l['watercolour_mockup'], 'walnut frame', l['walnut_frame_file'])

        #pyautogui.hotkey("ctrl", "q")  # Use "command" instead of "ctrl" on macOS

 
    def test(self):
       
        doc = self.app.documents.add()
        new_doc = doc.artLayers.add()
        text_color = ps.SolidColor()
        text_color.rgb.red = 0
        text_color.rgb.green = 255
        text_color.rgb.blue = 0
        new_text_layer = new_doc
        new_text_layer.kind = ps.LayerKind.TextLayer
        new_text_layer.textItem.contents = 'Hello, World!'
        new_text_layer.textItem.position = [160, 167]
        new_text_layer.textItem.size = 40
        new_text_layer.textItem.color = text_color
        options = ps.JPEGSaveOptions(12)
        # # save to jpg
        jpg = 'C:\\temp\\test.jpg'
        doc.saveAs(jpg, options, asCopy=True)
        self.app.doJavaScript(f'alert("save to jpg: {jpg}")')

    def process(self, filename):
        self.app.open(filename)

        pass

    def apply_action(self, action_name):
        idPly = self.app.charIDToTypeID("Ply ")
        desc8 = ps.ActionDescriptor()
        idnull = self.app.charIDToTypeID("null")
        ref3 = ps.ActionReference()
        idActn = self.app.charIDToTypeID("Actn")
        ref3.putName(idActn, action_name)
        idASet = self.app.charIDToTypeID("ASet")
        ref3.PutName(idASet, "Default Actions")
        desc8.putReference(idnull, ref3)
        self.app.executeAction(idPly, desc8, ps.DialogModes.DisplayNoDialogs)

    def open_file_run_action_save_file_close(self, source_filename, action_name, destination_filename):
        my_os.activate_window('Photoshop')
        self.app.open(source_filename)
        #time.sleep(2)
        self.apply_action(action_name)
        #time.sleep(2)
        self.save_as(destination_filename, 6)
        self.app.activeDocument.close()

class GoogleDrive:
    def __init__(
            self,
            ):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        CLIENT_SECRET_FILE = 'credentials.json'  # Your credentials JSON file
        TOKEN_PICKLE = 'token.pickle'  # Token storage file
        self.bing_artworks_folder_id =  '1EAIsdW2WJjBeftS8lX5E6ClO3LBxcR1q'
        self.to_process_folder_id = '1ZrfiSuRHm4A1GPCP3TLrTTxGqpvQ06Mx'
        self.no_of_files = 1000

        # Authenticate and create the Drive API service
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
        self.service = build('drive', 'v3', credentials=credentials)
        self.google_file_list = self.list_files_and_folders(self.bing_artworks_folder_id,self.no_of_files)
        pass

    def main(self):
        pass

    def list_files_and_folders(self, folder_id, no_of_files):
        # Define the scope of access
        #SCOPES = ['https://www.googleapis.com/auth/drive']

        # Define the API key
        

        # Build the service object
        

        # Get the resource object for files
        resource = self.service.files()

        # List N files in a folder using a query
        query = f"'{folder_id}' in parents"
        result = resource.list(pageSize=no_of_files, q=query, fields="files(id, name)").execute()

        # Get the file list from the result
        file_list = result.get('files')

        return(file_list)
    
    def download_image(self, file_id, destination_path):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print("Download progress: %d%%" % int(status.progress() * 100))

        print("Image downloaded successfully!")

    def search_filelist_by_name(self, needle:str)->dict:
        matches = [x for x in self.google_file_list if needle in x['name']]
        if matches:
            for x in matches:
                print('https://drive.google.com/file/d/' + x['id'],x['name'])
        return matches

class UpScale:
    def __init__(self):
        pass

    def upload_to_deepai(self, filename):
        r = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={
                'image': open(filename, 'rb'),
            },
            headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'},

        )
        response = r.json()
        return response['output_url']
    
    def main_job(self,p):
        print('upscale')
        filename = p['start_file']
        upscaled_image_url = my_upscale.upload_to_deepai(filename)
        my_os = OperatingSystem()
        my_os.get_remote_file(upscaled_image_url, p['local_upscaled_image'])

class WooCommerce():
    def __init__(self):
        self.base_url = "https://www.wonderwoodprints.co.uk/"
        self.wcapi = API(
            url= self.base_url,
            consumer_key = 'ck_d4e23641c2b2e40dd3bd8d2fecae8c9e4dc6a882',
            consumer_secret = 'cs_f4debf7ac5d7401494861bab60ea64d086240efe',
            version="wc/v3"
        )
        self.key = "jackdtowner@yahoo.co.uk"
        self.secret = "fFBA j7dQ UKqf BtDC 5qMU HG3v"


    def create_object_terms(self, new_terms_list:list, endpoint:str):
        all_terms = self.get_all_endpoint_terms(endpoint)
        not_in_terms_already = [x for x in new_terms_list if x.lower() not in [y['name'].lower() for y in all_terms]]
        my_new_terms = []
        all_terms_ids = []
        if not_in_terms_already != []:
            for new_item in not_in_terms_already:
                my_dict = {'name':new_item}
                my_new_terms.append(my_dict)
            r = self.wcapi.post(endpoint + 'batch',{'create':my_new_terms}) #create terms
            all_terms_ids = [{'id':x['id']} for x in r.json()['create']]
        all_terms_ids += [{'id':x['id']} for x in all_terms if x['name'].lower() in [y.lower() for y in new_terms_list]]
        return all_terms_ids

    def create_product(self, data):
        r = self.wcapi.post("products", data=data)
        return r

    def update_product(self, data):
        r = self.wcapi.put(f"products/{data['id']}", data=data)
        return r

    def update_single_product(self, product, new_product_info:dict):
        product['name'] = new_product_info[0]
        product['description'] = new_product_info[1]
        product['categories'] = self.create_object_terms(new_product_info[2],'products/categories/')
        product['tags'] == self.create_object_terms(new_product_info[3],'products/tags/')
        r = self.update_product(product)
        return r

    def create_wc_data(self):
        pass

    def delete_media_item(self, image_id:str):
        end_point = '/wp-json/wp/v2/media/' + str(image_id)
        url = self.base_url + end_point
        r = requests.delete(
            url=url,
            params = {'force': 'true'},
            auth=(self.key, self.secret)
        )
        return r

    def get_navigation_items(self):
        url = self.base_url + 'wp-json/wp/v2/menus/' 
        r = requests.get(
            url=url,
            auth=(self.key, self.secret)
        )
        return r
    
    def add_navigation_items(self):
        d = {
            'title':'hello',
            'url':'#',
            'menus':48,
        }
        url = self.base_url + 'wp-json/wp/v2/menus/menu-items' 
        r = requests.post(
            url=url,
            auth=(self.key, self.secret),
            data = d
        )   

    def add_alt_text_to_single_image(self, image_id:str, alt_text:str):
        end_point = '/wp-json/wp/v2/media/' + str(image_id)
        data = {'alt_text':alt_text}
        url = self.base_url + end_point
        res = requests.post(
            url=url,
            data=data,
            auth=(self.key, self.secret)
        )
        return res

    def add_alt_text_to_image(self, image_ids:list, alt_text:str):
        for image_id in image_ids:

            end_point = '/wp-json/wp/v2/media/' + str(image_id['id'])
            data = {'alt_text':alt_text}
            url = self.base_url + end_point
            res = requests.post(
                url=url,
                data=data,
                auth=(self.key, self.secret)
            )
        return res

    def upload_single_image(self, local_filename:str, remote_filename:str):
        data = open(local_filename, 'rb').read()
        url=self.base_url + '/wp-json/wp/v2/media/'
        res = requests.post(
            url=url,
            data=data,
            headers={ 
                'Content-Type': 'image/jpg',
                'Content-Disposition' : 'attachment; filename=%s'% remote_filename},
            auth=(self.key, self.secret),
            timeout=30
        )
        return res
    
    def upload_images(self, image_directory):

        images = [image for image in os.listdir(image_directory) if image.lower().endswith(('.jpg', '.jpeg', '.png'))]
        uploaded_ids = []
        for filename in images:
            if 'start' not in filename:
                full_filename = image_directory + "\\" + filename
                result = self.upload_single_image(full_filename).json()
                uploaded_ids.append({'id':result['id']})
        return uploaded_ids

    def main_job(self, product_info, p):
        print('woocommerce')
        categories_ids = my_wc.create_object_terms(product_info[0][2], 'products/categories/')
        tags_ids = my_wc.create_object_terms(product_info[0][3], 'products/tags/')
        my_image_ids = my_wc.upload_images(os.path.join(p['project_folder_stem'], p['project_folder']))
        r = my_wc.add_alt_text_to_image(my_image_ids, product_info[0][0])

        data = {
                'name': product_info[0][0],
                'description': product_info[0][1],
                'type': 'simple',
                'regular_price': '50.00',
                'images': my_image_ids,
                'categories':categories_ids,
                'tags':tags_ids,
            }
        
        result = my_wc.create_product(data)
        return result
    
    def get_product(self, id: str):
        r = self.wcapi.get("products/" + id)
        return r

    def get_all_endpoint_terms(self, endpoint):
        page = 1
        per_page = 100
        all_objects = []
        while True:
            response = self.wcapi.get(endpoint, params={'per_page':per_page, 'page':page})
            if response.status_code == 400 or response.status_code == 404 or response.json() == []:
                break
            all_objects += response.json()
            page += 1
        return all_objects

    def get_all_products(self):
        page = 1
        per_page = 50
        all_products = []
        while True:
            product_endpoint = 'products'
            response = self.wcapi.get(product_endpoint, params={'per_page':per_page, 'page':page})
            if response.status_code == 400 or response.json() == []:
                break
            all_products += response.json()
            page += 1
        return all_products

    def create_variations_json(self, post_id):
        p = self.get_product(post_id).json()['variations']
        my_list = [{'id':f'{x}'} for x in p]
        data = {'update':my_list}
        all_variation_data = self.wcapi.post(f"products/{post_id}/variations/batch", data=data).json()
        temp_variation_list = []
        for variation in all_variation_data['update']:
            new_variation = {
                'regular_price':variation['regular_price'],
                'price':variation['regular_price'],
                'attributes':variation['attributes']
            }
            temp_variation_list.append(new_variation)
        return temp_variation_list

    def test(self):

        # Create a variable product
        product_data = {
            "name": "Variable Product",
            "type": "variable",
            "regular_price": "20.00",
            "description": "This is a variable product",
            "short_description": "Variable product",
            "attributes": [
                {
                    "name": "Size",
                    "position": 0,
                    "visible": True,
                    "variation": True,
                    "options": ["Red", "Blue", "Green"]
                }
            ],
            }

        new_product = self.wcapi.post("products", product_data).json()

        # Create variations for the variable product
        variation_data = {'create':[
            {
                "attributes": [
                    {
                        "name": "Size",
                        "option": "Red"
                    }
                ],
                "regular_price": "22.00",
            },
            {
                "attributes": [
                    {
                        "name": "Size",
                        "option": "Blue"
                    }
                ],
                "regular_price": "25.00",
            }
        ]}

        
        a = self.wcapi.post(f"products/{new_product['id']}/variations/batch", data = variation_data)
        pass

    def get_all_products_and_update(self):
        all_products = self.get_all_products()
        for product in all_products[34:]:
            prompt_preamble = 'create extremely short description from following text: '
            prompt_descript = product['description']
            print(f'old descript: {my_oa.clean_string(prompt_descript)}')
            new_descript_ok = 'n'
            while new_descript_ok == 'n':
                new_description = my_oa.create_product_description_from_string(prompt_preamble, prompt_descript)
                print(new_description)
                new_descript_ok = input('OK? m(anual)/y/n/s(kip): ')
                if new_descript_ok == 's':
                    break
                elif new_descript_ok == 'y' or new_descript_ok == 'm':
                    if new_descript_ok == 'm':
                        new_description = input('manual:')
                    product['description'] = new_description
                    self.update_product(product)
                    break
                elif new_descript_ok == 'n':
                    prompt_preamble = 'create a very short alternative text for the following text: '
                    prompt_descript = new_description

    def create_product_based_on_template(self, data):
        print("Wordpress")
        
        template_product_id = '1084'
        template_variations = my_wc.wcapi.get(f"products/{template_product_id}/variations", params={'per_page': 100}).json()
        new_product = my_wc.get_product(template_product_id).json()
        new_product['images'] = []
        image_alt_text = "Product mockup for " + data['product_info'][0][0]
        
        print('Adding images')
        for prod_img in data['local_filenames']:
            local_file = data['local_filenames'][prod_img]
            remote_filename = local_file.split('\\')[-1]
            image_id = my_wc.upload_single_image(local_file, remote_filename).json()['id']
            self.add_alt_text_to_single_image(image_id, image_alt_text)
            if 'start' not in local_file: 
                new_product['images'].append({'id': image_id})
            else:
                download_image_id = image_id
        
        new_product['id'] = None
        new_product['type'] == 'variable'
        new_product['title'] = data['product_info'][0][0]
        new_product['name'] = data['product_info'][0][0]
        new_product['slug'] = ''
        new_product['permalink'] = ''
        new_product['date_created'] = ''
        new_product['date_created_gmt'] = ''
        new_product['date_modified'] = ''
        new_product['date_modified_gmt'] = ''
        new_product['sku'] = data['project_folder']
        new_product['variations'] = []
        new_product['related_ids'] = []
        new_product['description'] = data['product_info'][0][1]
        new_product['categories'] = my_wc.create_object_terms(data['product_info'][0][2], 'products/categories/')
        new_product['tags'] = my_wc.create_object_terms(data['product_info'][0][3], 'products/tags/')
        
        print('creating post')
        new_product = my_wc.wcapi.post(f"products/", new_product).json()

        template_map = [x for x in new_product['images']]

        for x in template_variations:
            x.pop('id')
            x.pop('sku')

        template_variations[0].update({'image': {'id':download_image_id}})
        template_variations[1].update({'image': {'id':[x['id'] for x in template_map if 'no_frame' in x['name']][0]}})
        template_variations[2].update({'image': {'id':[x['id'] for x in template_map if 'walnut' in x['name']][0]}})
        template_variations[3].update({'image': {'id':[x['id'] for x in template_map if 'white' in x['name']][0]}})
        template_variations[4].update({'image': {'id':[x['id'] for x in template_map if 'black' in x['name']][0]}})
        template_variations[5].update({'image': {'id':[x['id'] for x in template_map if 'oak' in x['name']][0]}})
        template_variations[6].update({'image': {'id':[x['id'] for x in template_map if 'magnet' in x['name']][0]}})

        print('updating variations')
        result = my_wc.wcapi.post(f"products/{new_product['id']}/variations/batch", {'create': template_variations})
        return

class my_openAI():
    def __init__(self):

        openai.organization = "org-zaJ7UbfSmPArIQwNAwpHQPfx"
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model="text-davinci-003"
        self.wc_combined_preamble_text = f"Create a json object with no text formatting, with a \
very short engaging SEO friendly woocommerce product title,\
a short punchy SEO friendly description,\
2 woocommerce categories,\
5 engaging social media tags,\
using the following keys 'title','description','categories','tags'\
based on the following text: "
    
    def get_text(self, prompt):
        response = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            temperature=0, 
            max_tokens=2000
        )
        return response.choices[0].text
    
    def create_product_description_from_string(self, preamble:str, product_description:str):
        """
        :param preamble: leave blank if creating product
        :return: describe what it returns
        """
        wc_combined_preamble_text = self.clean_string(preamble + f'{product_description}')
        wc_combined = self.clean_string(self.get_text(wc_combined_preamble_text))
        return wc_combined

    def clean_string(self, input_string):
        printable_pattern = r'<[^>]+>'
        cleaned_string = re.sub(printable_pattern, '', input_string)
        find_replace = [
            {'old':'Wood block'.lower(),'new':'wood block style'},
            {'old':'Woodblock'.lower(),'new':'wood block style'},
            {'old':'\n','new':''},
            {'old':'colors','new':'colours'},
            {'old':'2D','new':' '},
            {'old':'  ','new':' '}, #always last
        ]
        for x in find_replace:
            cleaned_string = cleaned_string.replace(x['old'], x['new'])
        return cleaned_string

    def create_product_json_from_string(self, product_description:str):
        printable_pattern = r'<[^>]+>'
        product_description = re.sub(printable_pattern, '', product_description)
        wc_combined_preamble_text = f'{product_description}. Remove all text formatting.'
        wc_combined = json.loads(self.get_text(wc_combined_preamble_text))
        wc_combined = list(wc_combined.values())  
        wc_combined[1] = self.remove_sentence_from_string('conversation', wc_combined[1])
        wc_combined[1] = wc_combined[1].replace('\n','')
        wc_combined[1] = wc_combined[1].replace('  ','')
        return wc_combined

    def remove_sentence_from_string(self,needle:str,haystack:str):
        updated_haystack = ".".join([x for x in haystack.split('.') if needle not in x])
        updated_haystack += '.' if updated_haystack[-1] != '.' else ''
        return updated_haystack

    def main_job(self, new_project_folder):
        print('openAI')
        wc_combined = self.create_product_json_from_string(self.wc_combined_preamble_text + new_project_folder.split('\\')[-1])
        return wc_combined
        #return [{x.split(':')[0].lower().replace(' ','_'):x.split(':')[1].strip()} for x in wc_combined.splitlines() if x]
        # wc_title = self.get_text(wc_title_preamble_text + p['project_folder'])
        # wc_description = self.get_text(wc_description_preamble_text + p['project_folder'])
        # wc_tags = self.get_text(wc_tags_preamble_text + wc_description)
        # wc_categories = self.get_text(wc_categories_preamble_text + wc_description)
        # return {
        #             'wc_title':wc_title,
        #             'wc_description':wc_description,
        #             'wc_tags':wc_tags,
        #             'wc_categories':wc_categories,

        #         }

class Vectorizer:
    def __init__(self):
        self.headers={
            'Authorization':
            'Basic dmthYmtueTc0a2FsZDJtOmpvaHBtNGdvb2dlbWliY2wzMDc5OHZqNWFxdGY2MDA5YTN0OGFjbjluNXUzNTg3NDdzbWI='
    }

    def vectorize_image(self, p):
        print('vectorize')
        response = requests.post(
            'https://vectorizer.ai/api/v1/vectorize',
            files={'image': open(p['local_upscaled_image'], 'rb')},
            data={
                # TODO: Add more upload options here
            },
            headers= self.headers,
        )
        if response.status_code == requests.codes.ok:
            # Save result
            with open(p['vectorized_image'], 'wb') as out:
                out.write(response.content)
        else:
            print("Error:", response.status_code, response.text)

def update_product_descriptions_for_existing_products():
    #get all products
    #for each product
    #get product details
    #update name, description, tags and categories
    #save
    my_wc = WooCommerce()
    my_oa = my_openAI()
    products = my_wc.get_all_endpoint_terms('products')
    for product in products[20:]:
        print(f"updating: {product['name']}")
        new_product_info = my_oa.create_product_json_from_description(product['description'])
        my_wc.update_single_product(product, new_product_info)

def update_google_drive():
    google_drive = GoogleDrive()
    no_of_files = 1
    bing_artworks_folder_id =  '1XSsH3D1N9AvzxNChdfWu5shwnIRAawdJ'
    bing_artworks_upload_to_wp_folder_id = '1EAIsdW2WJjBeftS8lX5E6ClO3LBxcR1q'
    google_file_list = google_drive.list_files_and_folders(folder_id=bing_artworks_folder_id,no_of_files=no_of_files)    
        
    local_folder_list =my_os.get_list_of_folders(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\Woodblock\\UPLOADED_TO_WP'))
    for local_folder in local_folder_list:
        local_folder_name = local_folder.split('\\')[-1]

        matching_google_file_id = [x['id'] for x in google_file_list if x['name'] == local_folder_name]
        if len(matching_google_file_id) > 0:
            file_id = matching_google_file_id[0]

            # Get the current parents of the file
            file = google_drive.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))

            # Move the file to the destination folder
            updated_file = google_drive.service.files().update(fileId=file_id, addParents=bing_artworks_upload_to_wp_folder_id, removeParents=bing_artworks_folder_id, fields='id, parents').execute()
            print(f"File moved to folder: {updated_file['parents']}")

def update_variations():
    product_payload = my_wc.get_product('1084')
    variations = my_wc.create_variations_json(post_id='1020')

    attributes = my_wc.get_product('1020').json()['attributes']
    data = {'id':'1084', 'attributes':attributes, 'variations':variations}
    my_wc.update_product()



def update_all_wc_new_image_and_variations():
    # Initialize WooCommerce, Photoshop, and Operating System instances
    my_wc = WooCommerce()
    my_ps = PhotoShop()
    my_os = OperatingSystem()

    # Initialize Photoshop application
    ps_app = ps.Application()

    # Define temporary folder and template product ID
    temp_folder = 'c:\\temp\\'
    template_product_id = '1084'

    # Fetch template variations from WooCommerce and remove 'sku' and 'id' fields
    template_variations = my_wc.wcapi.get(f"products/{template_product_id}/variations", params={'per_page': 100}).json()
    [template_variations[y].pop(x) for y in range(0, len(template_variations)) for x in ['sku', 'id' ]]

    # Fetch all products from WooCommerce
    products = my_wc.get_all_endpoint_terms('products')

    # Get template product details
    template_post = my_wc.get_product(template_product_id).json()

    temp_image = os.path.join(temp_folder,'temp.jpg')

    # Iterate through each product
    for product in products[1:]:
        print(f"updating: {product['name']}")
        
        # Download remote image to a local file
        remote_image = product['images'][0]['src']
        image_filename_stem = remote_image.split('/')[-1].split('0w')[0] 
        
        magnet_filename = image_filename_stem + 'magnetic.jpg'
        no_frame_filename = image_filename_stem + 'no_frame.jpg'
        black_frame_file = image_filename_stem + 'black.jpg'
        white_frame_file = image_filename_stem + 'white.jpg'
        oak_frame_file = image_filename_stem + 'oak.jpg'
        walnut_frame_file = image_filename_stem + 'walnut.jpg'
        
        
        local_magnet_file = os.path.join(temp_folder, magnet_filename)
        local_no_frame_file = os.path.join(temp_folder, no_frame_filename)
        local_black_frame_file = os.path.join(temp_folder, black_frame_file)
        local_white_frame_file = os.path.join(temp_folder, white_frame_file)
        local_oak_frame_file = os.path.join(temp_folder, oak_frame_file)
        local_walnut_frame_file = os.path.join(temp_folder, walnut_frame_file)
        
        
        my_os.get_remote_file(remote_image, temp_image)
        
        # Open the image using Photoshop
        print('Photoshop')
        my_ps.open_file_run_action_save_file_close(temp_image, 'magnetv2', local_magnet_file)
        my_ps.open_file_run_action_save_file_close(temp_image, 'no frame', local_no_frame_file)
        my_ps.open_file_run_action_save_file_close(temp_image, 'black frame', local_black_frame_file)
        my_ps.open_file_run_action_save_file_close(temp_image, 'white frame', local_white_frame_file)
        my_ps.open_file_run_action_save_file_close(temp_image, 'oak frame', local_oak_frame_file)
        my_ps.open_file_run_action_save_file_close(temp_image, 'walnut frame', local_walnut_frame_file)

        #delete the existing situ image
        print('deleting images')        
        image_strings_to_remove = ['situ', 'magnetic','no_frame','black','white','oak','walnut']
        for image_string in image_strings_to_remove:
            situ_image = [x for x in product['images'] if image_string in x['src']]
            if len(situ_image) > 0:
                product['images'].remove(situ_image[0])
                my_wc.delete_media_item(situ_image[0]['id'])    


        # Upload the modified image to WooCommerce and get the image ID
        print('Uploading images')
        magnetic_image_id = my_wc.upload_single_image(local_magnet_file, magnet_filename).json()['id']
        no_frame_image_id = my_wc.upload_single_image(local_no_frame_file, no_frame_filename).json()['id']
        black_frame_image_id = my_wc.upload_single_image(local_black_frame_file, black_frame_file).json()['id']
        white_frame_image_id = my_wc.upload_single_image(local_white_frame_file, white_frame_file).json()['id']
        oak_frame_image_id = my_wc.upload_single_image(local_oak_frame_file, oak_frame_file).json()['id']
        walnut_frame_image_id = my_wc.upload_single_image(local_walnut_frame_file, walnut_frame_file).json()['id']


        
        # Prepare data for updating the product in WooCommerce
        data = {
            'attributes': template_post['attributes'],
            'type': 'variable',
            'images': product['images'] + [{'id': magnetic_image_id}, 
                                           {'id': no_frame_image_id},
                                           {'id': black_frame_image_id},
                                           {'id': white_frame_image_id},
                                           {'id': oak_frame_image_id},
                                           {'id': walnut_frame_image_id},
                                           ]
        }
        
        # Update the product in WooCommerce
        my_wc.wcapi.put(f"products/{product['id']}", data)
        
        # Update the image ID in template variations
        template_variations[0].update({'image': {'id':product['images'][0]['id']}})
        template_variations[1].update({'image': {'id':no_frame_image_id}})
        template_variations[2].update({'image': {'id':walnut_frame_image_id}})
        template_variations[3].update({'image': {'id':white_frame_image_id}})
        template_variations[4].update({'image': {'id':black_frame_image_id}})
        template_variations[5].update({'image': {'id':oak_frame_image_id}})
        template_variations[6].update({'image': {'id':magnetic_image_id}})
        


        # Batch delete all existing variations for the product in WooCommerce
        my_wc.wcapi.post(f"products/{product['id']}/variations/batch", {'delete': product['variations']})


        # Batch create variations for the product in WooCommerce
        result = my_wc.wcapi.post(f"products/{product['id']}/variations/batch", {'create': template_variations})

        #clean up
        #remove local images

my_ps = PhotoShop()
my_oa = my_openAI()    
my_wc = WooCommerce()
my_os = OperatingSystem()
my_gd = GoogleDrive()


my_upscale = UpScale()
my_vectorize = Vectorizer()
#my_pi = PlaceItNet()


project_folder_stem = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents')
to_process_folder = os.path.join(project_folder_stem, 'TO PROCESS')
# Check if the folder exists


def run_complete_process_on_gdrive_to_process():
    #my_pi.login_to_place_net()
    no_of_files = 1000
    google_file_list = my_gd.list_files_and_folders(
        folder_id=my_gd.to_process_folder_id,
        no_of_files=no_of_files
    )    
    for google_file in google_file_list:
        google_file_name = google_file['name']
        print(google_file_name)
        destination_path = os.path.join(my_os.temp_folder,google_file['id'])
        start_file = '_start.jpg'
        product_info = my_oa.main_job(google_file_name), #create product info     
        product_title = "".join(x for x in product_info[0][0] if x.isalnum())

        my_os.create_folder(destination_path)

        file_names_params = {
            'start_file':start_file,
            'product_info':product_info,
            'product_title':product_title,
            'destination_path':destination_path
        }
      
        local_filenames = my_os.setup_filenames(file_names_params)
        
        my_gd.download_image(google_file['id'],local_filenames['destination_file_path'])
        p = {
            'project_folder_stem':os.path.join(my_os.temp_folder),
            'project_folder':google_file['id'],
            'local_filenames':local_filenames,
            'product_title':product_title,
            'start_file':start_file,
            'product_info':product_info,
        }
        my_ps.main_job(p)
        my_wc.create_product_based_on_template(p)
        print('next')


run_complete_process_on_gdrive_to_process()

if os.path.exists(to_process_folder):
    # Get a list of all files in the folder
    files = os.listdir(to_process_folder)
    my_pi.login_to_place_net()

    for file in files:
        project_folder = file.split('.')[0]
        new_project_folder = os.path.join(project_folder_stem, project_folder)
        if not os.path.exists(new_project_folder):
            print(project_folder)
            os.makedirs(new_project_folder)
            start_file = '_start.jpg'
            product_info = my_oa.main_job(new_project_folder) #create product info     
            product_title = "".join(x for x in list(product_info.values())[0] if x.isalnum())
            local_upscaled_image = os.path.join(new_project_folder,product_title+'-'+'high-res' + ".jpg")
            placeit_image_png = os.path.join(new_project_folder,product_title+'-'+  'insitu' + '.png')
            placeit_image_jpg = os.path.join(new_project_folder,product_title+'-'+ 'insitu' + '.jpg')
            source_file_path = os.path.join(to_process_folder,file)
            destination_file_path = os.path.join(new_project_folder,product_title+'-'+ start_file) #use this to for start image
            shutil.copy(source_file_path, destination_file_path)
            my_os.crop_image(destination_file_path,0.94)
            p = {
                'project_folder_stem':project_folder_stem,
                'project_folder':project_folder,
                'start_file':destination_file_path,
                'placeit_image_png':placeit_image_png,
                'placeit_image_jpg':placeit_image_jpg,
                'local_upscaled_image':local_upscaled_image,
                'vectorized_image':os.path.join(new_project_folder,product_title+'-'+'vector' + ".svg"),
                'watercolour-mockup':os.path.join(new_project_folder,product_title+'-'+'0watercolour' + ".jpg"),
                'watercolour-macro':os.path.join(new_project_folder,product_title+'-'+'watercolour-macro' + ".jpg"),
            }
            my_ps.main_job(p)
            #my_upscale.main_job(p)
            #my_vectorize.vectorize_image(p)
            my_pi.main_job(p)
            my_wc.main_job(product_info, p)
            print('next')
            
            


    



input('Finished')

