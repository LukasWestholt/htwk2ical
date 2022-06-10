from django.shortcuts import render
from django.urls import reverse
from config import is_maintenance, group_id_divider
from myapp1.models import GroupCache


def index(request):
    if is_maintenance:
        return render(request, 'index/maintenance.html')
    return render(request, 'index/index.html',
                  context={
                      "landing_page": True,
                      "divider": group_id_divider
                  })


def donate(request):
    amount_current = float(GroupCache.objects.get(key="donate_amount").value)
    amount_max = 50
    amount_percent = round(100 * amount_current / amount_max, 2)
    amount_current = "{:.2f} €".format(amount_current).replace(".", ",")
    amount_max = "{:.2f} €".format(amount_max).replace(".", ",")
    amount_heroku = "$9"
    return render(request, 'index/donate.html',
                  context={
                      "donate_page":    True,
                      "amount_current": amount_current,
                      "amount_max":     amount_max,
                      "amount_percent": amount_percent,
                      "amount_heroku":  amount_heroku
                  })


def donate_thx(request):
    return render(request, 'index/donate_thx.html')


def faq(request):
    faqs = [
        {
            "question": "Was genau ist jetzt dieses <em>HTWK2iCal</em>?",
            "answer":   "HTWK2iCal ist ein Tool, mit dem du dir deinen HTWK-Stundenplan in dein bevorzugtes "
                        "Kalender-Verwaltungs-Programm (Outlook, Google Kalender, etc.) holen kannst."
        },
        {
            "question": "Wie genau funktioniert das alles?",
            "answer":   "Du wählst deinen Studiengang aus und alle dazugehörigen Module, die angezeigt werden sollen."
                        "Dabei kannst du gern etwas wie \"Feiertage\" oder Wahlpflichtmodule, die du nicht belegt "
                        "hast, deaktivieren.<br />Zusätzlich kannst du die Namen der Module selbst bestimmen und "
                        "deinen Kalender dadurch übersichtlicher gestalten. So kannst du aus <em>\"Mathematik 2 MT-B "
                        "2. FS (pf) (Vp)\"</em> einfach <em>\"Mathe\"</em> machen.<br />Am Ende wird dir ein Link des "
                        "für dich erstellten Internetkalenders ausgespuckt. Sobald du mithilfe dieses Links einen "
                        "Kalender abonniert hast, bist du fertig."
        },
        {
            "question": "Ok, wie abonniere ich einen Kalender in Programm X?",
            "answer":   "###app-instructions###"
        },
        {
            "question": "Kalender abonnieren? Ich will den <em>downloaden</em>!",
            "answer":   "Das kannst du gern tun. Nachdem dein persönlicher Stundenplan erstellt wurde, hast du die "
                        "Möglichkeit ihn herunterzuladen. Außerdem kannst du ihn jederzeit herunterladen, wenn du den "
                        "generierten Link einfach in deinem Browser aufrufst.<br />Bedenke hierbei, dass "
                        "heruntergeladene Kalender bzw. Stundenpläne sich nicht aktualisieren werden. Das ist nur "
                        "möglich, wenn du den Kalender abonnierst."
        },
        {
            "question": "Ich belege zusätzlich Module aus anderen Studiengängen und möchte diese auch in meinem "
                        "Stundenplan haben.",
            "answer":   "Sobald du ankreuzen kannst, welche Module du in deinem Stundenplan haben möchtest und welche "
                        "nicht, solltest du auch einen fetten Button mit der Aufschrift \"Module aus anderem "
                        "Studiengang hinzufügen\" sehen. Dort einfach drauf klicken."
        },
        {
            "question": "Mein Kalender aktualisiert sich gar nicht!",
            "answer":   "Das liegt vermutlich daran, dass du ihn heruntergeladen statt abonniert hast. Automatisch "
                        "aktualisieren können sich nur Kalender, die du abonniert hast."
        },
        {
            "question": "Ich gebe den Namen meines Studiengangs ein, aber bekomme immer die Meldung <em>\"Bitte wähle "
                        "einen "
                        "gültigen Studiengang!\"</em>.",
            "answer":   "Solang du einen Studiengang aus der Liste wählst, die erscheint, sobald du ein paar Zeichen "
                        "tippst, sollte alles funktionieren. Falls es das nicht tut, <a href=" + reverse('contact') +
                        ">gib mir Bescheid</a>."
        },
        {
            "question": "Wie lange ist mein Stundenplan bzw. der Link dorthin gültig?",
            "answer":   "Ganz einfach: solange der Stundenplan über die HTWK-Seite zur Verfügung steht. Das bedeutet, "
                        "dass dein Link mit dem Ende des Semesters ungültig wird. Entsprechend wird er danach nicht "
                        "mehr funktionieren."
        },
        {
            "question": "Was kostet mich der Spaß?",
            "answer":   "Nichts. Hammer, oder?<br />Mein einsames Programmierer-Ego freut sich aber jederzeit über "
                        "<a href=" + reverse('contact') + ">Lob und Anregungen</a>.<br />Sollte dir HTWK2iCal dein "
                                                          "Studienleben etwas vereinfachen, kannst du außerdem gern "
                                                          "<a href=" + reverse('donate') + ">etwas zur Tilgung der "
                                                                                           "Betriebskosten beitragen"
                                                                                           "</a>."
        }
    ]
    return render(request, 'index/faq.html', context={"faq_page": True, "faqs": faqs})


def contact(request):
    return render(request, 'index/contact.html', context={"contact_page": True})


def maintenance(request):
    return render(request, 'index/maintenance.html',
                  context={'start_date': '01.04.', 'term_str': 'Sommersemester 2022'})


def imprint(request):
    return render(request, 'index/imprint.html')


def privacy(request):
    return render(request, 'index/privacy.html')
