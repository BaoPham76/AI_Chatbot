from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from datetime import datetime, timedelta
from unidecode import unidecode

import requests

from .database import get_product_details, get_order_details, get_brands, get_watches_by_rating

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
        cust_sex = tracker.get_slot("cust_sex")

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
            dispatcher.utter_message(text=f"Xin vui lòng cho {bot_position} biết tên của {cust_sex} ạ.")
            return [SlotSet('cust_sex', name_cap(cust_sex))]

        response = f"Kính chào {cust_sex} {cust_name}. WatchStyle có thể giúp gì được {cust_sex} {cust_name} ạ?"
        dispatcher.utter_message(text=response)
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


class ActionSelectWatch(Action):

    # Đặt tên cho hành động, sẽ được tham chiếu trong các tệp như `domain.yml` và `stories.yml`
    def name(self) -> Text:
        return "action_recommend_watch"

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
                id, product_name, price_sell, img = row
                formatted_price = f"{price_sell:,.0f}".replace(",", ".") + " VNĐ"
                product_link = f"http://127.0.0.1:8000/product-detail/{id}"
                response += (
                    f"Sản phẩm: {product_name}\n"
                    f"Giá: {formatted_price}\n"
                    f"![Ảnh sản phẩm](http://127.0.0.1:8000/asset/client/images/products/small/{img})\n"
                    f"Xem chi tiết tại: [Here!]({product_link})\n\n"
                )

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
            total_money, order_status, created_at, name, phone_number, city, district, ward, apartment_number = order_data
            created_at_dt = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
            estimated_delivery_dt = created_at_dt + timedelta(days=7)
            estimated_delivery = estimated_delivery_dt.strftime("%d/%m/%Y")
            name_text = name[0] + '*' * (len(name) - 2) + name[-1] if len(name) > 2 else name
            phone_text = phone_number[:3] + '*' * (len(phone_number) - 2) + phone_number[-2:]
            status_text = {
                0: "Chờ xử lý",
                1: "Đang giao hàng",
                2: "Đã hủy",
                3: "Đã nhận hàng"
            }.get(order_status, "Không xác định")
            city_name = get_province_name(city)

            ward_name = get_ward_name(district, ward)
            response = (
                f"Trạng thái: {status_text}.\n"
                f"Dự kiến giao hàng: {estimated_delivery}.\n"
                f"Tên : {name_text}\n"
                f"SDT : {phone_text}\n"
                #bỏ ward name để che dấu huyện, nếu cần thì thêm vào
                f"Địa chỉ: {apartment_number}, *****, *****, {city_name}\n"


            )
        else:
            response = f"Không tìm thấy thông tin cho mã đơn hàng {order_id}. Vui lòng kiểm tra lại mã đơn hàng của bạn."

        # Gửi phản hồi cho người dùng
        dispatcher.utter_message(text=response)
        return [SlotSet("order_id", None)]



# GHN API Token
GHN_TOKEN = '5ba2f299-3fee-11ef-8de7-a6386691fa55'

# Helper functions to get city, district, and ward names from GHN API
def get_province_name(province_id):
    response = requests.get(
        'https://online-gateway.ghn.vn/shiip/public-api/master-data/province',
        headers={'token': GHN_TOKEN}
    )
    provinces = response.json().get('data', [])
    # Convert both province_id and ProvinceID to string for comparison
    for province in provinces:
        if str(province['ProvinceID']) == str(province_id):  # Compare as strings
            return province['ProvinceName']
    return "Không xác định"


def get_ward_name(district_id, ward_id):
    response = requests.get(
        'https://online-gateway.ghn.vn/shiip/public-api/master-data/ward',
        headers={'token': GHN_TOKEN},
        params={'district_id': district_id}
    )
    wards = response.json().get('data', [])
    for ward in wards:
        if ward['WardCode'] == ward_id:
            return ward['WardName']
    return "Không xác định"


class ActionShowWatchBrands(Action):

    def name(self) -> str:
        return "action_show_watch_brands"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> list:
        # Gọi phương thức get_brands từ database.py để lấy danh sách thương hiệu
        brands = get_brands()

        # Tạo các nút bấm cho mỗi thương hiệu
        buttons = [{"title": brand, "payload": f'Tôi chọn {brand}'} for brand in brands]

        # Gửi thông báo đến người dùng với danh sách các thương hiệu
        dispatcher.utter_message(
            text="Chọn một thương hiệu đồng hồ bạn muốn mua.",
            buttons=buttons
        )
        return []


class ActionShowWatchesByRating(Action):
    def name(self) -> Text:
        return "action_show_watches_by_rating"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy giá trị rating từ user input
        rating = next(tracker.get_latest_entity_values("rating"), None)
        if rating:
            try:
                # Loại bỏ dấu và chuẩn hóa input
                normalized_rating = unidecode(rating.lower())

                # Từ điển chuyển chữ thành số
                word_to_number = {
                    "mot": 1, "hai": 2, "ba": 3, "bon": 4, "nam": 5,
                    "sau": 6, "bay": 7, "tam": 8, "chin": 9, "muoi": 10
                }

                # Nếu rating là số, chuyển đổi trực tiếp; nếu là chữ, chuyển từ chữ sang số
                if normalized_rating.isdigit():
                    min_rating = int(normalized_rating)
                else:
                    min_rating = word_to_number.get(normalized_rating)

                if min_rating is None:
                    raise ValueError("Invalid rating")

                # Gọi hàm từ file database.py để lấy danh sách đồng hồ theo rating
                results = get_watches_by_rating(min_rating)

                if results:
                    response = ""
                    # Duyệt qua các kết quả tìm thấy và tạo câu trả lời cho người dùng
                    for row in results:
                        product_id, product_name, price_sell, img, total_reviews, average_rating = row
                        product_link = f"http://127.0.0.1:8000/product-detail/{product_id}"
                        response += (
                            f"Sản phẩm: {product_name}\n"
                            f"Giá: {price_sell} VND\n"
                            f"Đánh giá trung bình: {average_rating:.1f} sao\n"
                            f"Tổng số đánh giá: {total_reviews}\n"
                            f"![Ảnh sản phẩm](http://127.0.0.1:8000/asset/client/images/products/small/{img})\n"
                            f"Xem chi tiết tại: [Here!]({product_link})\n\n"
                        )
                else:
                    # Không tìm thấy sản phẩm với mức đánh giá mong muốn
                    response = f"Không tìm thấy đồng hồ nào được đánh giá từ {min_rating} sao trở lên."
            except ValueError:
                response = "Vui lòng nhập số sao hợp lệ (ví dụ: 4 sao, 5 sao)."
        else:
            response = "Bạn muốn tìm đồng hồ được đánh giá mấy sao?"

        # Trả lời người dùng với thông tin đã tìm được hoặc thông báo lỗi
        dispatcher.utter_message(text=response)
        return []
