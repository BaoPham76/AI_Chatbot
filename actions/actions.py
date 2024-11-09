from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta

from .database import get_product_details, get_order_details

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

class action_save_cust_info(Action):
    def name(self):
        return 'action_save_cust_info'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = (tracker.current_state())["sender_id"]

        # Extract customer name and sex from entities
        cust_name = next(tracker.get_latest_entity_values("cust_name"), None)
        cust_sex = next(tracker.get_latest_entity_values("cust_sex"), None)

        bot_position = "Em"
        if cust_sex is None:
            cust_sex = "Bạn"

        if cust_sex in ["Anh", "Chị"]:
            bot_position = "Em"
        elif cust_sex in ["Cô", "Chú", "Ông", "Bà"]:
            bot_position = "Cháu"
        else:
            cust_sex = "Bạn"
            bot_position = "Em"

        if not cust_name:
            dispatcher.utter_message(text="Xin vui lòng cho tôi biết tên của quý khách.")
            return []

        print(cust_sex + " " + cust_name + ", " + bot_position)
        # Set slots with extracted and formatted values
        return [
            SlotSet('cust_name', f" {name_cap(cust_name)}"),
            SlotSet('cust_sex', name_cap(cust_sex)),
            SlotSet('bot_position', name_cap(bot_position))
        ]
class ActionSaveBrand(Action):

    def name(self) -> Text:
        return "action_save_brand"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy thương hiệu từ entities
        brand = next(tracker.get_latest_entity_values("brand"), None)

        # Kiểm tra xem có thương hiệu không
        if brand:
            return [SlotSet('brand', brand)]
        return []

class ActionSaveGender(Action):

    def name(self) -> Text:
        return "action_save_gender"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy thương hiệu từ entities
        gender = next(tracker.get_latest_entity_values("gender"), None)

        # Kiểm tra xem có thương hiệu không
        if gender:
            return [SlotSet('gender', gender)]
        return []
# Hành động tìm kiếm thông tin sản phẩm
# class ActionGetProductDetails(Action):
#
#     # Đặt tên cho hành động, sẽ được tham chiếu trong các tệp như `domain.yml` và `stories.yml`
#     def name(self) -> Text:
#         return "action_get_product_details"
#
#     # Thực thi hành động khi người dùng yêu cầu thông tin sản phẩm
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         # Lấy tên sản phẩm từ các thực thể trong câu người dùng nhập
#         product_name = next(tracker.get_latest_entity_values("product_name"), None)
#         print(f"Tên sản phẩm nhận được: {product_name}")
#
#         # Kiểm tra xem người dùng có cung cấp tên sản phẩm hay không
#         if not product_name:
#             dispatcher.utter_message(text="Xin lỗi, tôi không hiểu bạn đang hỏi về sản phẩm nào.")
#             return []
#
#         # Gọi hàm từ file database.py để lấy thông tin chi tiết sản phẩm
#         results = get_product_details(product_name)
#
#         # Xử lý kết quả truy vấn từ cơ sở dữ liệu
#         if results:
#             response = ""
#             # Duyệt qua các kết quả tìm thấy và tạo câu trả lời cho người dùng
#             row = results[0]
#             product_name, price_sell, img = row
#             response += f"Sản phẩm: {product_name}\nGiá: {price_sell} VND\n![Ảnh sản phẩm](http://127.0.0.1:8000/asset/client/images/products/small/{img})\n"
#
#         else:
#             # Nếu không tìm thấy sản phẩm, thông báo lỗi
#             response = f"Không tìm thấy sản phẩm với tên '{product_name}'"
#
#         # Trả lời người dùng với thông tin đã tìm được hoặc thông báo lỗi
#         dispatcher.utter_message(text=response)
#
#         return []


class ActionSelectWatch(Action):

    # Đặt tên cho hành động, sẽ được tham chiếu trong các tệp như `domain.yml` và `stories.yml`
    def name(self) -> Text:
        return "action_select_watch"

    # Thực thi hành động khi người dùng yêu cầu thông tin sản phẩm
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy thương hiệu và giới tính từ các thực thể trong câu người dùng nhập
        brand = tracker.get_slot("brand")
        gender = tracker.get_slot("gender")

        # Nếu chưa có `brand`, yêu cầu người dùng cung cấp
        if not brand:
            dispatcher.utter_message(
                text="Bạn muốn mua đồng hồ của hãng nào? Có thể là Casio, Citizen, Seiko, hoặc hãng khác mà bạn thích?")
            return [SlotSet("brand", brand)]

        # Nếu chưa có `gender`, yêu cầu người dùng cung cấp
        if not gender:
            dispatcher.utter_message(text="Bạn muốn tìm đồng hồ cho Nam, Nữ, hay Unisex?")
            return [SlotSet("gender", gender)]

        # Gọi hàm từ file database.py để lấy thông tin chi tiết sản phẩm với brand và gender
        results = get_product_details(brand, gender)

        # Xử lý kết quả truy vấn từ cơ sở dữ liệu
        if results:
            response = ""
            # Duyệt qua các kết quả tìm thấy và tạo câu trả lời cho người dùng
            for row in results:
                product_name, price_sell, img = row
                response += f"Sản phẩm: {product_name}\nGiá: {price_sell} VND\n![Ảnh sản phẩm](http://127.0.0.1:8000/asset/client/images/products/small/{img})\n"

        else:
            # Nếu không tìm thấy sản phẩm, thông báo lỗi
            response = f"Không tìm thấy sản phẩm với thương hiệu {brand} và giới tính {gender}."

        # Trả lời người dùng với thông tin đã tìm được hoặc thông báo lỗi
        dispatcher.utter_message(text=response)

        return []

class ActionTrackOrder(Action):

    def name(self) -> Text:
        return "action_track_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy mã đơn hàng từ slot
        order_id = tracker.get_slot("order_id")

        # Kiểm tra xem mã đơn hàng có được cung cấp không
        if not order_id:
            dispatcher.utter_message(text="Vui lòng cung cấp mã đơn hàng để tôi có thể kiểm tra.")
            return []

        # Gọi hàm lấy thông tin đơn hàng từ database.py
        order_data = get_order_details(order_id)

        # Xử lý kết quả từ cơ sở dữ liệu
        if order_data:
            total_money, order_status, created_at, name, phone_number, city, district, ward, aparment_number = order_data
            created_at_dt = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
            estimated_delivery_dt = created_at_dt + timedelta(days=7)
            estimated_delivery = estimated_delivery_dt.strftime("%d/%m/%Y")
            response = (
                f"Đơn hàng của bạn hiện đang ở trạng thái: {order_status}. "
                f"Dự kiến giao hàng: {estimated_delivery}."
            )
        else:
            response = f"Không tìm thấy thông tin cho mã đơn hàng {order_id}. Vui lòng kiểm tra lại mã đơn hàng của bạn."

        # Gửi phản hồi cho người dùng
        dispatcher.utter_message(text=response)

        return []


