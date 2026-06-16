from .models import Course


class Cart:
    SESSION_KEY = 'bornes_cart'

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = {}
            self.session[self.SESSION_KEY] = cart
        self.cart = cart

    def add(self, course):
        key = str(course.id)
        if key not in self.cart:
            self.cart[key] = {
                'course_id': course.id,
                'title': course.title,
                'price': course.price,
                'instructor': course.instructor,
            }
            self.save()
            return True
        return False

    def remove(self, course_id):
        key = str(course_id)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        del self.session[self.SESSION_KEY]
        self.save()

    def save(self):
        self.session.modified = True

    def __len__(self):
        return len(self.cart)

    def __iter__(self):
        course_ids = [int(k) for k in self.cart.keys()]
        courses = Course.objects.filter(id__in=course_ids)
        course_map = {str(c.id): c for c in courses}
        for key, item in self.cart.items():
            item = item.copy()
            item['course'] = course_map.get(key)
            yield item

    def total_price(self):
        return sum(item['price'] for item in self.cart.values())

    def contains(self, course_id):
        return str(course_id) in self.cart

    def get_items(self):
        return list(self)
