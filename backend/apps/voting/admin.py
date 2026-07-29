from django.contrib import admin

from apps.voting.models import Poll, PollBallotReceipt, PollOption, PollVote


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("title", "visibility", "opens_at", "closes_at", "quorum", "created_at")
    list_filter = ("visibility",)
    search_fields = ("title",)
    inlines = [PollOptionInline]


@admin.register(PollBallotReceipt)
class PollBallotReceiptAdmin(admin.ModelAdmin):
    list_display = ("poll", "user", "created_at")
    search_fields = ("user__username",)


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ("poll", "option", "created_at")
