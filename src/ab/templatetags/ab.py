from django.template.base import Library
from django.template.base import Node
from django.template.base import TemplateSyntaxError
from django.template.base import Variable

from ab import VARIANT_A
from ab import VARIANT_B
from ab.models import ABTest


register = Library()



@register.tag
def run_ab_test(parser, token):
    """
    Declare an AB test in the template:

    {% run_ab_test "Name of the test" %}
        <!-- markup for variant A goes here -->
    {% or %}
        <!-- markup for variant B goes here -->
    {% end_ab_test %}
    """
    arguments = token.split_contents()
    tag_name = arguments.pop(0)

    if len(arguments) != 1:
        raise TemplateSyntaxError("")

    ab_test_name = arguments[0]

    variant_a_content = parser.parse(("or",))
    parser.delete_first_token()

    end_tag_marker = "end_{}".format(tag_name.split("_", 1)[1])
    variant_b_content = parser.parse((end_tag_marker,))
    parser.delete_first_token()


    return _ABTestNode(ab_test_name, variant_a_content, variant_b_content)


class _ABTestNode(Node):

    def __init__(self, ab_test_name, variant_a_content, variant_b_content):
        self.ab_test_name = Variable(ab_test_name)
        self.variant_a_content = variant_a_content
        self.variant_b_content = variant_b_content

    def render(self, context):
        ab_test_name = self.ab_test_name.resolve(context)
        ab_test = ABTest.objects.get_or_create(name=ab_test_name)[0]

        block_context = context.copy()
        block_context["ab_test"] = ab_test

        if self._is_variant_a_applicable(context["request"]):
            block_context["ab_test_variant"] = VARIANT_A
            content = self.variant_a_content.render(block_context)
            ab_test.times_a_presented += 1
        else:
            block_context["ab_test_variant"] = VARIANT_B
            content = self.variant_b_content.render(block_context)
            ab_test.times_b_presented += 1

        ab_test.save()

        return content

    @staticmethod
    def _is_variant_a_applicable(request):
        raise NotImplementedError("Determine whether A or B is applicable!")
