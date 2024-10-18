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

def get_product_details(product_name):
    #Truy vấn sản phẩm từ cơ sở dữ liệu dựa trên tên sản phẩm
    connection = create_connection()
    cursor = connection.cursor()

    # Truy vấn tìm sản phẩm dựa trên tên
    query = f"SELECT name, price_sell, img FROM products WHERE name LIKE '%{product_name}%'"
    cursor.execute(query)

    # Đọc kết quả
    results = cursor.fetchall()

    # Đóng kết nối
    cursor.close()
    connection.close()

    return results
