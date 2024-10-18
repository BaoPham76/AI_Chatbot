from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from .database import get_product_details


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet



#Viết hoa chữ cái đầu tiên
def name_cap(text):
    tarr = text.split()
    for idx in range(len(tarr)):
        tarr[idx] = tarr[idx].capitalize()
    return ' '.join(tarr)

#Lưu thông tin khách hàng
class action_save_cust_info(Action):
    #Đặt tên cho actions
    def name(self):
        return 'action_save_cust_info'

    #Thực thi hành động khi cần lưu thông tin khách hàng
    def run(self, dispatcher, tracker, domain):
        user_id = (tracker.current_state())["sender_id"]
        print(user_id)

        #Lấy tên và giới tính khách hàng từ các thực thể (entities) đã nhận diện
        cust_name = next(tracker.get_latest_entity_values("cust_name"), None)
        cust_sex = next(tracker.get_latest_entity_values("cust_sex"), None)
        bot_position = "Em"

        if cust_sex is  None:
            cust_sex = "Quý khách"

        if (cust_sex == "anh") | (cust_sex == "chị"):
           bot_position = "em"
        elif (cust_sex == "cô") | (cust_sex == "chú"):
            bot_position = "cháu"
        else:
            cust_sex = "Quý khách"
            bot_position = "Em"

        if not cust_name:
            #dispatcher.utter_template("utter_greet_name",tracker)
            return []

        print (name_cap(cust_name))
        #Trả về các slot đã được cập nhật bao gồm tên, giới tính và vị trí của bot (cách xưng hô)
        return [SlotSet('cust_name', " "+name_cap(cust_name)),SlotSet('cust_sex', name_cap(cust_sex)),SlotSet('bot_position', name_cap(bot_position))]


# Hành động tìm kiếm thông tin sản phẩm
class ActionGetProductDetails(Action):

    # Đặt tên cho hành động, sẽ được tham chiếu trong các tệp như `domain.yml` và `stories.yml`
    def name(self) -> Text:
        return "action_get_product_details"

    # Thực thi hành động khi người dùng yêu cầu thông tin sản phẩm
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy tên sản phẩm từ các thực thể trong câu người dùng nhập
        product_name = next(tracker.get_latest_entity_values("product_name"), None)

        # Kiểm tra xem người dùng có cung cấp tên sản phẩm hay không
        if not product_name:
            dispatcher.utter_message(text="Xin lỗi, tôi không hiểu bạn đang hỏi về sản phẩm nào.")
            return []

        # Gọi hàm từ file database.py để lấy thông tin chi tiết sản phẩm
        results = get_product_details(product_name)

        # Xử lý kết quả truy vấn từ cơ sở dữ liệu
        if results:
            response = ""
            # Duyệt qua các kết quả tìm thấy và tạo câu trả lời cho người dùng
            for row in results:
                product_name, price_sell, img = row
                response += f"Sản phẩm: {product_name}\nGiá: {price_sell} VND\nẢnh: {img}\n---\n"
        else:
            # Nếu không tìm thấy sản phẩm, thông báo lỗi
            response = f"Không tìm thấy sản phẩm với tên '{product_name}'"

        # Trả lời người dùng với thông tin đã tìm được hoặc thông báo lỗi
        dispatcher.utter_message(text=response)

        return []

