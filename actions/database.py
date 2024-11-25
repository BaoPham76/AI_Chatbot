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
    query = "SELECT id, name, price_sell, img FROM products WHERE name LIKE %s"
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

def get_brands():
    """Truy vấn danh sách thương hiệu từ cơ sở dữ liệu"""
    # Kết nối đến cơ sở dữ liệu
    connection = create_connection()
    cursor = connection.cursor()

    # Truy vấn danh sách thương hiệu
    query = "SELECT name FROM brands WHERE deleted_at IS NULL"
    cursor.execute(query)

    # Lấy kết quả
    results = cursor.fetchall()

    # Đóng kết nối
    cursor.close()
    connection.close()

    return [row[0] for row in results]

def get_watches_by_rating(min_rating):
    """
    Lấy danh sách các sản phẩm có tổng số lượng đánh giá từ một mức sao trở lên.
    :param min_rating: Số sao tối thiểu (ví dụ: 4 sao)
    :return: Danh sách các sản phẩm và tổng đánh giá
    """
    # Kết nối đến cơ sở dữ liệu
    connection = create_connection()
    cursor = connection.cursor()

    # Truy vấn để lấy danh sách sản phẩm
    query = """
        SELECT 
            products.id, 
            products.name, 
            products.price_sell, 
            products.img,
            COUNT(*) AS total_reviews, 
            AVG(product_reviews.rating) AS average_rating
        FROM 
            products
        JOIN 
            product_reviews 
        ON 
            products.id = product_reviews.product_id
        WHERE 
            product_reviews.rating >= %s
        AND 
            product_reviews.deleted_at IS NULL
        GROUP BY 
            products.id, 
            products.name, 
            products.price_sell
        HAVING 
            total_reviews > 0
        ORDER BY 
            average_rating DESC
    """
    cursor.execute(query, (min_rating,))

    # Đọc kết quả
    results = cursor.fetchall()

    # Đóng kết nối
    cursor.close()
    connection.close()

    return results
