# JustEat - Food Ordering Platform

A comprehensive Django-based food ordering platform that connects customers with restaurants, featuring role-based authentication, order management, and feedback systems.

## 🍽️ Features

### Customer Features
- **Restaurant Discovery**: Browse and search restaurants by name, cuisine, location, and price
- **Smart Recommendations**: Personalized restaurant suggestions based on preferences
- **Menu Management**: View detailed menus with prices and descriptions
- **Shopping Cart**: Add items to cart and manage quantities
- **Order Tracking**: Real-time order status updates
- **Order History**: Complete order history with search functionality
- **Profile Management**: Update personal information and preferences
- **Reviews & Ratings**: Rate and review restaurants after completing orders
- **Feedback System**: Submit feedback and track responses from restaurant officials

### Restaurant Owner Features
- **Restaurant Registration**: Register and manage restaurant details
- **Menu Management**: Add, edit, and delete food items with special deals
- **Order Processing**: Manage incoming orders and update status
- **Analytics Dashboard**: View sales insights and performance metrics
- **Feedback Management**: Respond to customer feedback and queries
- **Inventory Tracking**: Monitor popular items and sales trends

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.2+
- PostgreSQL (recommended) or SQLite

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NamanRestaurant-main
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your database settings
   DATABASE_URL=postgresql://user:password@localhost:5432/naman_restaurant
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python manage.py seed_data
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Use the sample credentials or create new accounts

## 🔐 Sample Credentials

After running `python manage.py seed_data`, you can use these credentials:

### Restaurant Owner
- **Username**: `isf_owner`
- **Password**: `owner@123`

### Sample Customers
- **Username**: `user1` | **Password**: `user@12345`

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests
python manage.py test


### Test Coverage
The application includes comprehensive unit tests covering:
- **Models**: Database model validation and relationships
- **Views**: HTTP request handling and response generation
- **Forms**: Form validation and data processing
- **Authentication**: Login, logout, and permission checks
- **Business Logic**: Order processing, cart management, and recommendations

## 📊 Database Schema

The application uses the following main models:

### Core Models
- **User**: Django's built-in user model
- **Restaurant**: Restaurant information and details
- **FoodItem**: Menu items with pricing and descriptions
- **Order**: Customer orders with status tracking
- **OrderItem**: Individual items within orders
- **Review**: Customer reviews and ratings
- **Feedback**: Customer feedback and restaurant responses
- **UserProfile**: Extended user information and preferences

### Key Relationships
- One-to-Many: Restaurant → FoodItem, Restaurant → Order, User → Order
- Many-to-Many: User → Favorite Restaurants, User → Cuisine Preferences
- Foreign Keys: Order → Restaurant, OrderItem → FoodItem, Review → Restaurant

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/naman_restaurant

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False

# Email (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static Files
STATIC_URL=/static/
STATIC_ROOT=staticfiles/
```

### Logging Configuration
The application includes comprehensive logging:
- **Console Logging**: Real-time development feedback
- **File Logging**: Persistent logs in `logs/app.log`
- **Log Levels**: INFO, WARNING, ERROR with appropriate handlers
- **Log Rotation**: Automatic log file rotation (5MB max, 5 backups)

## 🎨 UI/UX Features

### Design Principles
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Modern Aesthetics**: Clean, professional interface with smooth animations
- **User-Friendly**: Intuitive navigation and clear visual hierarchy
- **Accessibility**: Proper contrast ratios and keyboard navigation

### Key UI Components
- **Restaurant Cards**: Hover effects with description overlays
- **Smart Recommendations**: Compact, visually appealing recommendation section
- **Interactive Elements**: Smooth transitions and hover states
- **Toast Notifications**: Non-intrusive success/error messages
- **Pagination**: Clean, accessible pagination controls

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure email settings
5. Set up logging for production
6. Run security checks: `python manage.py check --deploy`

### Docker Deployment (Optional)
```bash
# Build and run with Docker
docker-compose up --build
```

## 📝 API Documentation

### Key Endpoints
- `GET /restaurants/` - List all restaurants
- `GET /restaurant/<id>/menu/` - View restaurant menu
- `POST /cart/add/` - Add item to cart
- `POST /orders/place/` - Place new order
- `GET /orders/` - View order history
- `POST /restaurant/<id>/review/` - Submit review

### Authentication
- Session-based authentication
- Role-based permissions (Customer/Restaurant Owner)
- CSRF protection on all forms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test cases for usage examples

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added feedback system and enhanced UI
- **v1.2.0**: Improved logging and comprehensive testing

---

**Built using Django, Bootstrap, and modern web technologies.**