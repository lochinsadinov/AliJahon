import graphene
from graphene_django import DjangoObjectType

from apps.models import Region

class BookType(DjangoObjectType):
    class Meta:
        model = Region
        fields = ("id", "name")

class Query(graphene.ObjectType):
    questions = graphene.List(BookType)
    question_by_id = graphene.Field(BookType, id=graphene.String())

    def resolve_questions(root, info, **kwargs):
        # Querying a list
        return Region.objects.all()

    def resolve_question_by_id(root, info, id):
        # Querying a single question
        return Region.objects.get(pk=id)


schema=graphene.Schema(query=Query)