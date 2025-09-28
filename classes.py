"""
Examples of Regular Python Classes and Record Designs

This file demonstrates different approaches to class design in Python:
1. Traditional classes with manual implementation
2. Dataclasses (modern record-style approach)
3. NamedTuple (immutable records)
4. Pydantic models (with validation)
5. Attrs classes (third-party alternative)
"""

from dataclasses import dataclass, field, replace
from typing import List, Optional, NamedTuple, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum
import datetime

# =============================================================================
# 1. TRADITIONAL PYTHON CLASSES
# =============================================================================

class Person:
    """Traditional class with manual __init__, __str__, and __repr__"""
    
    def __init__(self, name: str, age: int, email: str = ""):
        self.name = name
        self.age = age
        self.email = email
        self._created_at = datetime.datetime.now()
    
    def __str__(self) -> str:
        return f"Person(name='{self.name}', age={self.age})"
    
    def __repr__(self) -> str:
        return f"Person(name='{self.name}', age={self.age}, email='{self.email}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Person):
            return False
        return (self.name == other.name and 
                self.age == other.age and 
                self.email == other.email)
    
    def is_adult(self) -> bool:
        return self.age >= 18
    
    def get_age_in_years(self) -> int:
        return self.age


class BankAccount:
    """Traditional class with private attributes and methods"""
    
    def __init__(self, account_number: str, owner: Person, initial_balance: float = 0.0):
        self.account_number = account_number
        self.owner = owner
        self._balance = initial_balance  # Private attribute
        self._transaction_history: List[Dict[str, Any]] = []
    
    @property
    def balance(self) -> float:
        """Read-only property for balance"""
        return self._balance
    
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self._balance += amount
        self._add_transaction("deposit", amount)
    
    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if self._balance >= amount:
            self._balance -= amount
            self._add_transaction("withdrawal", amount)
            return True
        return False
    
    def _add_transaction(self, transaction_type: str, amount: float) -> None:
        """Private method to record transactions"""
        self._transaction_history.append({
            "type": transaction_type,
            "amount": amount,
            "timestamp": datetime.datetime.now(),
            "balance_after": self._balance
        })
    
    def get_statement(self) -> List[Dict[str, Any]]:
        return self._transaction_history.copy()


class Shape(ABC):
    """Abstract base class demonstrating inheritance"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def area(self) -> float:
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        pass
    
    def describe(self) -> str:
        return f"{self.name} with area {self.area():.2f} and perimeter {self.perimeter():.2f}"


class Rectangle(Shape):
    """Concrete implementation of Shape"""
    
    def __init__(self, width: float, height: float):
        super().__init__("Rectangle")
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    """Another concrete implementation of Shape"""
    
    def __init__(self, radius: float):
        super().__init__("Circle")
        self.radius = radius
    
    def area(self) -> float:
        return 3.14159 * self.radius ** 2
    
    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius


# =============================================================================
# 2. DATACLASSES (Modern Record-Style)
# =============================================================================

@dataclass
class Point:
    """Simple dataclass for 2D coordinates"""
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def translate(self, dx: float, dy: float) -> 'Point':
        return Point(self.x + dx, self.y + dy)


@dataclass
class Student:
    """Dataclass with default values and post-init processing"""
    name: str
    student_id: str
    grades: List[float] = field(default_factory=list)
    enrollment_date: datetime.date = field(default_factory=datetime.date.today)
    is_active: bool = True
    
    def __post_init__(self):
        # Validation and processing after initialization
        if not self.name.strip():
            raise ValueError("Student name cannot be empty")
        if not self.student_id.strip():
            raise ValueError("Student ID cannot be empty")
    
    @property
    def gpa(self) -> float:
        return sum(self.grades) / len(self.grades) if self.grades else 0.0
    
    def add_grade(self, grade: float) -> None:
        if 0 <= grade <= 4.0:
            self.grades.append(grade)
        else:
            raise ValueError("Grade must be between 0 and 4.0")


@dataclass(frozen=True)  # Immutable dataclass
class Coordinate:
    """Immutable coordinate class"""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")


@dataclass
class Product:
    """Complex dataclass with various field options"""
    name: str
    price: float
    category: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict, repr=False)  # Don't show in repr
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now, init=False)  # Not in __init__
    
    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price cannot be negative")
    
    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
    
    def apply_discount(self, percentage: float) -> 'Product':
        """Returns a new Product with discounted price"""
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100")
        
        new_price = self.price * (1 - percentage / 100)
        return replace(self, price=new_price)


# =============================================================================
# 3. NAMEDTUPLE (Immutable Records)
# =============================================================================

class Color(NamedTuple):
    """Immutable color representation using NamedTuple"""
    red: int
    green: int
    blue: int
    alpha: float = 1.0
    
    def to_hex(self) -> str:
        """Convert to hexadecimal representation"""
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"
    
    def with_alpha(self, alpha: float) -> 'Color':
        """Return a new Color with different alpha"""
        return self._replace(alpha=alpha)


class Dimension(NamedTuple):
    """Immutable dimension record"""
    width: float
    height: float
    depth: float
    
    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth
    
    @property
    def surface_area(self) -> float:
        return 2 * (self.width * self.height + 
                   self.width * self.depth + 
                   self.height * self.depth)


# =============================================================================
# 4. ENUMS AND STATUS CLASSES
# =============================================================================

class OrderStatus(Enum):
    """Enumeration for order status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Order class using enum for status"""
    order_id: str
    customer_name: str
    items: List[str]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def confirm(self) -> None:
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CONFIRMED
        else:
            raise ValueError("Order can only be confirmed from pending status")
    
    def ship(self) -> None:
        if self.status == OrderStatus.CONFIRMED:
            self.status = OrderStatus.SHIPPED
        else:
            raise ValueError("Order can only be shipped from confirmed status")


# =============================================================================
# 5. ADVANCED PATTERNS
# =============================================================================

@dataclass
class Node:
    """Generic node for tree structures"""
    value: Any
    children: List['Node'] = field(default_factory=list)
    parent: Optional['Node'] = None
    
    def add_child(self, child: 'Node') -> None:
        child.parent = self
        self.children.append(child)
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def is_root(self) -> bool:
        return self.parent is None


class Builder:
    """Builder pattern example"""
    
    def __init__(self):
        self.reset()
    
    def reset(self) -> 'Builder':
        self._data = {}
        return self
    
    def with_name(self, name: str) -> 'Builder':
        self._data['name'] = name
        return self
    
    def with_age(self, age: int) -> 'Builder':
        self._data['age'] = age
        return self
    
    def with_email(self, email: str) -> 'Builder':
        self._data['email'] = email
        return self
    
    def build(self) -> Person:
        if 'name' not in self._data or 'age' not in self._data:
            raise ValueError("Name and age are required")
        return Person(**self._data)


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def demonstrate_classes():
    """Function to demonstrate all class types"""
    
    print("=== Traditional Classes ===")
    person = Person("Alice", 30, "alice@example.com")
    print(person)
    print(f"Is adult: {person.is_adult()}")
    
    account = BankAccount("123456", person, 1000.0)
    account.deposit(500.0)
    account.withdraw(200.0)
    print(f"Balance: ${account.balance}")
    
    rect = Rectangle(5, 3)
    circle = Circle(2)
    print(rect.describe())
    print(circle.describe())
    
    print("\n=== Dataclasses ===")
    point = Point(3.0, 4.0)
    print(f"Point: {point}")
    print(f"Distance from origin: {point.distance_from_origin():.2f}")
    
    student = Student("Bob", "S12345")
    student.add_grade(3.5)
    student.add_grade(3.8)
    print(f"Student: {student}")
    print(f"GPA: {student.gpa:.2f}")
    
    coord = Coordinate(40.7128, -74.0060)  # NYC coordinates
    print(f"NYC Coordinates: {coord}")
    
    product = Product("Laptop", 999.99, "Electronics", ["computer", "portable"])
    print(f"Product: {product}")
    discounted = product.apply_discount(10)
    print(f"Discounted: {discounted}")
    
    print("\n=== NamedTuple ===")
    red_color = Color(255, 0, 0)
    print(f"Red color: {red_color}")
    print(f"Hex: {red_color.to_hex()}")
    
    box = Dimension(10, 5, 3)
    print(f"Box dimensions: {box}")
    print(f"Volume: {box.volume}")
    
    print("\n=== Enums and Status ===")
    order = Order("ORD-001", "Charlie", ["Book", "Pen"], 25.99)
    print(f"Order: {order}")
    order.confirm()
    order.ship()
    print(f"Updated order status: {order.status}")
    
    print("\n=== Builder Pattern ===")
    builder = Builder()
    built_person = (builder
                   .with_name("David")
                   .with_age(25)
                   .with_email("david@example.com")
                   .build())
    print(f"Built person: {built_person}")


if __name__ == "__main__":
    demonstrate_classes()
