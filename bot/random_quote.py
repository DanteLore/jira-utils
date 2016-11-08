import random


class RandomQuote:
    def __init__(self):
        random.seed()

    beginnings = [
        "I'll tell you something: ",
        "You know what? ",
        'A great man once said "',
        "Sure, Jira is important, but ",
        "The thing is... ",
        "Maybe I've said this before, but ",
        "Check this out: ",
        'In times of trouble, remember these immortal words "',
        "Joking aside people, ",
        "You guys need to stop hating and remember: ",
        "Whoah there, my friend. ",
        "Call me old fashioned, but I've always said \"",
        "Wait wait wait wait... ",
        "Hold the phone! ",
        "",
        'My mother always told me "',
        'You might be busy, but just stop for a moment and consider this: '
    ]
    middles = [
        "Our highest priority is to satisfy the customer through early and continuous delivery of valuable software",
        "Welcome changing requirements, even late in development. Agile processes harness change for the customer's competitive advantage",
        "Deliver working software frequently, from a couple of weeks to a couple of months, with a preference to the shorter timescale",
        "Business people and developers must work together daily throughout the project",
        "Build projects around motivated individuals. Give them the environment and support they need, and trust them to get the job done",
        "The most efficient and effective method of conveying information to and within a development team is face-to-face conversation",
        "Working software is the primary measure of progress",
        "Agile processes promote sustainable development. The sponsors, developers, and users should be able to maintain a constant pace indefinitely",
        "Continuous attention to technical excellence and good design enhances agility",
        "Simplicity - the art of maximising the amount of work *not* done - is essential",
        "The best architectures, requirements, and designs emerge from self-organising teams",
        "At regular intervals, the team reflects on how to become more effective, then tunes and adjusts its behaviour accordingly"
    ]
    ends = [
        " and no mistake!",
        " or so I heard anyway",
        " or something like that...",
        " and _that's_ how _we_ roll",
        ". Amen to that!",
        ". Oh that's so true!",
        ". YES!",
        ". *GOT THAT?*",
        ". You can't mess with the Agile Principles",
        ". You *know* it's true. For real.",
        ". 20 years on and the Agile Principals are still so poignant :cry:",
        " :partyparrot:",
        ". *JiraBot* over and out.",
        ". And if you don't agree you'd better start getting your CV in order. #justsayin",
        ". You know it makes sense.",
        " or we could just go back to Waterfall. You decide.",
        " and I ain't playin'",
        " for real.",
        " and you know it makes sense",
        ". You can't argue with that... if you want to carry on working with me at least.",
        " #justsayin",
        "... unless you have any better ideas?",
        ". *JiraBot* EXIT STAGE LEFT",
        ". I hope that clarifies things",
        ". Search your soul - is that truly the way we've been working?"
    ]

    def get_quote(self):
        b = random.choice(self.beginnings)
        m = random.choice(self.middles)
        e = random.choice(self.ends)

        if b.endswith('"'):
            m += '"'
        elif len(b) > 0 and not (b.strip().endswith('.') or b.strip().endswith('?')):
            m = m[0].lower() + m[1:]

        if random.randint(50) == 0:
            return ["{0}{1}{2}".format(b, m, e)]
        else:
            return []
