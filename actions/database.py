import mysql.connector

def create_connection():
    #Kết nối đến cơ sở dữ liệu MySQL
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',  # Thay với user của bạn
        password='',  # Thay với mật khẩu của bạn
        database='project_test'  # Tên database của bạn
    )
    return connection

def get_product_details(brand, gender):
    #Truy vấn sản phẩm từ cơ sở dữ liệu dựa trên tên sản phẩm
    connection = create_connection()
    cursor = connection.cursor()

    # Truy vấn tìm sản phẩm dựa trên tên
    query = "SELECT name, price_sell, img FROM products WHERE name LIKE %s"
    cursor.execute(query, (f"{brand} - {gender}%",))

    # Đọc kết quả
    results = cursor.fetchall()

    # Đóng kết nối
    cursor.close()
    connection.close()

    return results


def get_order_details(order_id):
    # Kết nối đến cơ sở dữ liệu
    connection = create_connection()
    cursor = connection.cursor()

    # Truy vấn để lấy thông tin đơn hàng
    query = "SELECT total_money, order_status, created_at, name, phone_number, city, district, ward, apartment_number FROM orders WHERE id = %s"
    cursor.execute(query, (order_id,))

    # Đọc kết quả
    result = cursor.fetchone()

    # Đóng kết nối
    cursor.close()
    connection.close()

    return result
