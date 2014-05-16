#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Auskunftsgenerator -- zwecks (halbwegs) einfachem deployment alles in
# einer Datei.
#
# Wenn das wirklich jemand anpassen will, sollte er/sie vorher mit
# datenschutzgruppe@rote-hilfe.de sprechen.  Man mÃ¼sste wohl drÃ¼ber
# nachdenken, wie die Operationen sinnvoll parametrisiert werden kÃ¶nnen,
# um den Kram anpassbar zu machen, ohne dass das deployment richtig
# unangenehm wird.
# 
# Der Quelltext und die enthaltenen Daten sind public domain.  Wer den
# Kram verbessert und die Verbesserungen nicht an die Allgemeinheit
# zurÃ¼ckgibt, ist trotzdem ein Schuft.


import cgi 
import re
import os 
import sys
import tempfile

class Error(Exception):
	pass


PRE_BLA = u"""<h1>Generator fÃ¼r Auskunftsersuchen</h1>
<p>Auf dieser Seite kÃ¶nnt ihr automatisch Auskunftsersuchen an
Polizei und Verfassungsschutz erzeugen lassen -- fÃ¼llt einfach
die Felder unten aus, wÃ¤hlt die Stellen, an die ihr Anfragen
stellen wollt und klickt auf "Ok".  Ihr solltet dann ein PDF zurÃ¼ckkriegen,
das ihr nur noch ausdrucken und unterschreiben mÃ¼sst.  
Wenn euer Drucker halbwegs ok ist, dÃ¼rften die Briefe zur Verwendung mit
FensterumschlÃ¤gen taugen.  Bei der Gelegenheit: Die BehÃ¶rden brauchen
manchmal ein bisschen, aber Tricks mit "verlorenen" Briefen sind uns nie
zu Ohren gekommen.  In dem Sinn kÃ¶nnt ihr euch das Geld fÃ¼r Einschreiben
wahrscheinlich sparen.</p>

<p>FÃ¼r manche der BehÃ¶rden unten hat die Erfahrung gezeigt, dass auch
fÃ¼r NegativauskÃ¼nfte Ausweiskopien angefordert werden.  In diesen FÃ¤llen
(sind mit FuÃŸnote markiert) weisen wir in den Anschreiben auf eine
Ausweiskopie in der Anlage hin -- steckt sie einfach mit in den
Umschlag.  Diese Kopie muss nicht beglaubigt sein.</p>

<p>Ihr kÃ¶nnt auf der Kopie die Daten, die nicht unmittelbar zur
IdentitÃ¤tsprÃ¼fung dienen, schwÃ¤rzen.  SchwÃ¤rzen dÃ¼rft ihr insbesondere
die Ausweisnummer, GrÃ¶ÃŸe und Augenfarbe, das Ausstellungsdatum und die
ausstellende BehÃ¶rde sowie die StaatsangehÃ¶rigkeit.</p>

<p><strong>Sind meine Daten hier sicher?</strong> Die Daten, die ihr hier
eingebt, werden bei uns nur fÃ¼r den 
Moment gespeichert, den wir zur Verarbeitung brauchen.  Wenn euch das
trotzdem unheimlich ist, kÃ¶nnt ihr die Felder auch leer lassen.  Wir
erzeugen dann Platzhalter, in die ihr eure Daten dann per Hand eintragen
kÃ¶nnt.  Wenn ihr -- <a href="/cgi-bin/moin.cgi/AuskunftErsuchen">was
wir empfehlen</a> -- Ã¼ber https auf diesen Server
zugreift, sind die Daten auch wÃ¤hrend des Transports durchs Netz
(weitgehend) sicher.  Zu den Verkehrsdaten vgl. unsere <a
href="/privacy.html">Privacy Policy</a>.</p>
<p><strong>Werden Polizei und Verfassungsschutz durch die Anfrage nicht
erst auf mich aufmerksam?</strong>  MÃ¶glich ist das sicher, aber:
<ul><li>Der behÃ¶rdliche Missbrauch von Datenbanken ist letztlich nur durch
Herstellung von Ã–ffentlichkeit zu beschrÃ¤nken.  Der Nutzen Ã¼berwiegt
ein mÃ¶glicherweise vorhandenes Restrisiko bei weitem.</li>
<li>Wenn gegen euch etwas vorliegt, ist das Auskunftsersuchen sicher
kein aufregendes Datum fÃ¼r die BehÃ¶rden mehr ("X sorgt sich um informationelle
Selbstbestimmung" -- Wow!).  Liegt nichts gegen euch vor, ist 
nicht damit zu rechnen, dass eigens ein Datensatz eingerichtet 
wird, schon, weil so etwas allenfalls in den kÃ¼hnsten Spudok-Dateien auch
nur im Entferntesten zu rechtfertigen wÃ¤re (und die BehÃ¶rde aufs Dach bekommen
wÃ¼rde, wenn der/die zustÃ¤ndige Datenschutzbeauftragte dahinterkÃ¤me -- ok,
dieser Einwand ist schwach...)</li>
<li>Die Information, dass jemand ein Auskunftsersuchen gestellt hat,
wird fÃ¼r die BehÃ¶rden um so uninteressanter, je mehr Leute Auskunftsersuchen
stellen (zumal die Trennung zwischen Geeks, Anarchos, BÃ¼rgerrechtlerInnen
usf. auch nicht einfach sein wird).</li>
<li>Wir raten ausdrÃ¼cklich davon ab, irgendwelche GrÃ¼nde Ã¼ber
die automatisch generierten hinaus in den Anfragen anzugeben.
Dies ist nach der gegenwÃ¤rtigen Rechtslage in den meisten
FÃ¤llen nicht nÃ¶tig.  Ausnahmen sind unten notiert, und fÃ¼r diese
kÃ¶nnen keine Ersuchen generiert werden.  Wer viel Zeit und Kraft
hat, kÃ¶nnte die Vereinbarkeit von Regelungen des Typs "besonderes
Interesse muss angegeben werden" mit der Verfassung prÃ¼fen lassen.
Wir wÃ¼rden bei so einem Prozess helfen, so gut wir kÃ¶nnen.</li>
</ul>

<p><strong>Was passiert, wenn ich den Kram abschicke?</strong>
Typisches Verhalten umfasst folgende drei Prototypen: Entweder, ihr
bekommt gleich einen Bescheid, dass nichts Ã¼ber euch vorliegt, oder ihr
bekommt nach ein paar Wochen einen solchen Bescheid (in diesen FÃ¤llen
ist anzunehmen, dass den BehÃ¶rden einige ihrer Daten zu heiÃŸ fÃ¼r die
Auskunft vorkamen).  SchlieÃŸlich kann auch relativ schnell (typisch ist
wohl eine Woche) eine Aufforderung zum Einsenden einer Kopie eueres
Personalausweises.  Je nach BehÃ¶rde und Mondphase kommt aber auch alle
denkbaren Variationen vor.  Auch variiert, ob die BehÃ¶rden beglaubigte
oder bestÃ¤tigte
Kopien verlangen oder nicht (das BKA etwa tut das leider).</p>

<p>Nebenbei: Eure Polizeidienststelle vor Ort kann die evtl. von den
BehÃ¶rden geforderte BestÃ¤tigung vornehmen und sollte dafÃ¼r kein Geld
verlangen.  Wenn die nicht wissen, wovon ihr redet, sagt ihnen, dass sie
bei der Telefonnummer anrufen sollen, die (hoffentlich) auf der Antwort
der BehÃ¶rde angegeben ist.</p>

<p>Auf <a href="http://auskunftsersuchen.info/">auskunftsersuchen.info</a>
gibt es eine schÃ¶ne Ãœbersicht Ã¼ber die Handlungsweisen der einzelnen
BehÃ¶rden.</p>

<p><strong>Sie wollen GrÃ¼nde?!</strong>  Wenn euch Polizeien nach
GrÃ¼nden fÃ¼r euer Auskunftersuchen fragen, wendet euch bitte gleich an
uns.  So gehts nÃ¤mlich nicht: Deals des Typs "Info gegen Info" sind im
Geiste des VolkszÃ¤hlungsurteils und letztlich auch aller Polizeigesetze
nicht statthaft.  Bei den Geheimdiensten ist die Situation leider
anders, was gerade angesichts des skandalÃ¶sen Verhaltens (und auch des
ganzen Prinzips) extrem Ã¤rgerlich ist.  Doch auch bei denen gilt:
<em>Nie spezifische GrÃ¼nde angeben, das wollen wir gar nicht erst
einreiÃŸen lassen.</em>  AuÃŸer, ihr wisst ganz genau, was ihr tut (es
schadet nicht, sich mit uns zu beraten, wenn ihr GrÃ¼nde angeben
wollt).</p>

<p><strong>Helft uns.</strong>  Beteiligt euch an <a
href="/moin/FrontPage">an unserem Wiki</a> zu Ãœberwachung und
Datenschutz (nutzt auch die 
<a href="/moin/AuskunftErsuchen">Wiki-Seite zum
Auskunftsersuchen</a>), teilt uns mit,
was aus euren Anfragen geworden ist, verbessert unsere Formbriefe,
entwerft neue an BehÃ¶rden, die wir bisher noch nicht berÃ¼cksichtigt haben
und schickt sie uns.  Vielen Dank.</p>
"""

POST_BLA = u"""
<hr align="left" width="20%">
<p><a name="rem1"><sup>1</sup></a> Diese BehÃ¶rden verlangen zur Erteilung
einer Auskunft die Angabe von AnlÃ¤ssen oder einem "besonderen Interesse".
Es ist nicht akzeptabel, dass hier die Preisgabe mÃ¶glicherweise
sensibler Informationen fÃ¼r die Wahrung des Grundrechts auf informationelle
Selbstbestimmung verlangt wird.  Solange den betreffenden BehÃ¶rden diese
Sorte Rechtsbruch erlaubt wird (und das wÃ¤re wohl nur durch erheblichen
Ã¶ffentlichen Druck zu Ã¤ndern) haben Anfragen wenig oder keinen Sinn.</p>
<p><a name="rem2"><sup>2</sup></a> Die SIS-Kontaktstellen sollten
alle identische AuskÃ¼nfte geben.  Es dÃ¼rfte also wenig sinnvoll sein,
an mehrere der SIS-Stellen Auskunftsersuchen zu stellen.</p>

<p><a name="rem3"><sup>3</sup></a> Von diesen Einrichtungen ist bekannt, dass
sie selbst fÃ¼r NegativauskÃ¼nfte Ausweiskopien verlangen (was zunÃ¤chst
nicht zu beanstanden ist).  Auf den
Formularen steht deshalb gleich "Anlage: Ausweiskopie".  Diese muss aber
nicht bestÃ¤tigt sein.  Viele BehÃ¶rden (BKA, etliche LKÃ„) verlangen 
inzwischen fÃ¼r alles bestÃ¤tigte Kopien; das vermerken wir hier nicht.  
Wenn die schon die Sorte Terror machen, sollen sie jedenfalls immer 
noch einen Extrabrief schreiben mÃ¼ssen, mit dem mensch dann auch bei 
der Polizeidienststelle bessere Karten hat.</p>

<p><a name="rem4"><sup>4</sup></a> Das BKA ist die Kontaktstelle zu den
EU-Datenbanken in der BRD; insofern geht sowohl die SIS- also auch die
BKA-Anfrage an eine Stelle.  Wenn ihr beide Auskunftersuchen abschickt,
wÃ¼rde sich ein gemeinsamer Umschlag anbieten...</p>
<p><a name="rem6"><sup>6</sup></a> Diese Einrichtungen beschrÃ¤nken das
kostenlose Auskunftsrecht explizit auf einmal "pro Jahr" (auch andere
Einrichtungen werden allerdings wohl ungehalten, wenn ihr deutlich Ã¶fter
nachfragt).</p>
<p><a name="rem7"><sup>7</sup></a> Auch Auskunfteien verlangen
dann und wann Kopien von Personalausweisen.  Im Gegensatz zur
Situation bei der Polizei ist hier die Haltung der
Datenschutzbeauftragten recht eindeutig skeptisch; insbesondere ist hier
die SchwÃ¤rzung aller Angaben auÃŸer Name, Anschrift, Geburtsdatum und
GÃ¼ltigkeitsdauer statthaft.  <a href="http://www.bfdi.bund.de/SharedDocs/Publikationen/AusweiskopieAuskunftsersuchen.html?nn=408908">Details
vom BfDI</a></p>

<hr>
<address><a
href="mailto:datenschutzgruppe@rote-hilfe.de">datenschutzgruppe@rote-hilfe.de</a>
</address>"""


BASE_TEMPLATE = u"""<html>
<head><title>Generator fÃ¼r Auskunftsersuchen</title></head>
<style type="text/css"><!--
p.lol { 
	margin-top:2px; margin-bottom:2px; width:200px}
h2.lol { 
	font-size:130%; margin-bottom:4px; background:black; color:white;}
h3.lol { 
	font-size:110%; font-style:italic; margin-bottom:3px; margin-top:4px;}
div.row { 
	display: table-row}
div.column { 
	display: table-cell;padding-right: 0.5em;}
p.warning {
	margin-left:2em;
	padding-left:4pt;
	border-left:1pt solid red;
	font-style: italic;}
.formlabel {
	background-color: #eeeeee;
}
.formfield {
	background-color: #cccccc;
}
dl.formitems dt {
	width: 12em;
	position: relative;
	top: 8pt;
}
dl.formitems dd {
	margin-left: 0pt;
	padding-left: 12em;
	padding-top: 2pt;
	padding-bottom: 2pt;
}
--></style>
<body>
$!httpWarning!
$!preBla!
$|getForm|
$!postBla!
</body>"""


FORM_TEMPLATE = u"""
<form action="$[scriptName]/auskunft.pdf" method="POST" autocomplete="off">
	<dl class="formitems">
		<dt class="formlabel">Vorname</dt>
		<dd class="formfield"><input name="vorname" size="30"></dd>
		<dt class="formlabel">Nachname</dt>
		<dd class="formfield"><input name="nachname" size="40"></dd>
		<dt class="formlabel">StraÃŸe und Hausnummer</dt>
		<dd class="formfield"><input name="adresse" size="60"></dd>
		<dt class="formlabel">Postleitzahl</dt>
		<dd class="formfield"><input name="plz" size="5"></dd>
		<dt class="formlabel">Ort</dt>
		<dd class="formfield"><input name="ort" size="50"></dd>
		<dt class="formlabel">Geboren am</dt>
		<dd class="formfield"><input name="gebdat" size="15"></dd>
		<dt class="formlabel">Geburtsort</dt>
		<dd class="formfield"><input name="gebort" size="50"></dd>
		</dl>
		<div style="background:#eeeeee">
		<p><strong>Generiere Briefe an:</strong></p> 
		$!selection!
		<p align="right">
		<input style="width:200px;height:60px;font-weight:bold" 
			type="submit" value="Generieren"></p>
		</div>
		</form>"""


LETTER_MENU_TEMPLATE = u"""
<div class="row">
<div class="column">
	$!Bund!
	$!International!
	$!Private!
</div>
<div class="column">
	$!LÃ¤nder!
</div>
<div class="column">
	$!Ã–sterreich!
</div>
</div>"""

os.environ["PATH"] = os.environ["PATH"]+":/usr/local/bin:/usr/local/bin/tex"


####################### Hilfsfunktionen.

def texToPdf(teXSource, dviPsOptions="", filesToLinkBackTo=[]):
	owd = os.getcwd()
	wdName = tempfile.mkdtemp("texToPs")
	teXSource = teXSource.encode("utf-8", "replace")

	try:
		os.chdir(wdName)
		for fname in filesToLinkBackTo:
			os.symlink(os.path.join(owd, fname), fname)
#		open("/tmp/tmp.tex", "w").write(teXSource.encode("utf-8", "replace")
		with open("tmp.tex", "w") as f:
			f.write(teXSource)
		os.system("latex --interaction scrollmode tmp.tex > /dev/null 2>&1")
#		os.system("latex --interaction scrollmode tmp.tex 1>&2")
		f = os.popen("dvips %s -o - tmp.dvi "
			"| ps2pdf -sPAPERSIZE=a4 - - "%dviPsOptions)
		pdfCode = f.read()
		if f.close() is not None:
			raise Error("PDF-Erzeugung schlug fehl.")
	finally:
		os.chdir(owd)
		os.system("rm -rf '%s'"%wdName)
	return pdfCode


def escapePCDATA(val):
	if val is None:
		return ""

	return unicode(val
		).replace("&", "&amp;"
		).replace('<', '&lt;'
		).replace('>', '&gt;'
		).replace("\0", "&x00;")


def escapeAttrVal(val):
	"""returns val with escapes for double-quoted attribute values.
	"""
	if val is None:
		return '""'
	return escapePCDATA(val).replace('"', '&quot;')


class Template(object):
	"""a *very* basic and ad-hoc template engine.

	It works on HTML strings, with the following constructs expanded:

	* $[key] -- value for key, escaped for double-quoted att values
	* $(key) -- value for key, escaped for PCDATA
	* $|func| -- replace with the value of func(vars)
	* $!raw! -- value for key, non-escaped (other template ops are expanded)
	* $$ -- a $ char.

	Use either unicode strings or plain ASCII
	"""
	def __init__(self, source):
		self.source = unicode(source)

	def render(self, vars):
		"""returns a string with the template filled using vars.

		vars is a dictionary mapping keys to unicode-able objects.

		You'll get back a unicode string that you must encode before
		spitting it out to the web.
		"""
		return re.sub(r"\$\$", "$",
			re.sub(r"\$\|([a-zA-Z0-9_]+)\|", 
				lambda mat: globals()[mat.group(1)](vars),
			re.sub(r"\$\(([a-zA-Z0-9_]+)\)", 
				lambda mat: escapePCDATA(vars.get(mat.group(1), "")),
			re.sub(r"\$\[([a-zA-Z0-9_]+)\]", 
				lambda mat: escapeAttrVal(vars.get(mat.group(1), "")),
			re.sub(ur"\$!([a-zA-ZÃ„Ã–ÃœÃ¤Ã¶Ã¼ÃŸ0-9_]+)!", 
				lambda mat: unicode(vars.get(mat.group(1), "")),
			self.source)))))

	def serve(self, vars):
		"""emits a basic CGI response for this template.
		"""
		payload = self.render(vars
			).encode("utf-8"
		# did you know all text/bla MIMEs have to use CRLF as line
		# separators?
			).replace("\n", "\r\n")

		sys.stdout.write(
			"content-type: text/html;charset=utf-8\r\n"
			"content-length: %d\r\n\r\n"
			"%s"%(len(payload), payload))


def httpFatalError(errmsg):
	"""emits a last-resport error message.

	errmsg must be some sort of string.  If it's not unicode, the content
	will be interpreted as iso latin 1.
	"""
	if isinstance(errmsg, unicode):
		errmsg = errmsg.encode("iso-8859-1", "replace")

	sys.stdout.write("\n".join([
		"content-type: text/html;charset=iso-8859-1\n",
		"<html><head><title>Fehler</title></head>",
		"<body><p>Da ist ein Fehler passiert:</p>",
		"<p>%s</p>"%errmsg,
		'<p>Wenn ihr nicht versteht, warum dieser Fehler aufgetreten'
		' ist, fragt bei <a href="mailto:datenschutzgruppe@rotehilfe.de">',
		'datenschutzgruppe@rotehilfe.de</a> nach.</p></body></html>']
		).replace("\n", "\r\n"))
	sys.exit()


def makePdf(personalData, letterKeys):
	texSource = (TEX_HEADER+(
		u"\n\n".join([LETTERS[key][-1] for key in letterKeys])
		)+"\\end{document}\n")%personalData
	return texToPdf(texSource)


####################### LaTeX-Quellen

TEX_HEADER = unicode(r"""
\documentclass[
  DIN,
  paper=a4,
  BCOR=0mm,
  DIV=15,
  headlines=4,
  parskip=false,
  fromalign=right,
  fromaddrfield=true,
  backaddress=%(haveBackAddress)s,
  foldmarks=true,
  fontsize=10pt,
  enlargefirstpage=yes,
  firstfoot=no,
  locfield=wide,
  fromurl=true,
	ngerman,
	USenglish
  ] {scrlttr2}
\usepackage[utf8]{inputenc}
\usepackage{babel}
\renewcommand{\familydefault}{cmss}
\newcommand{\ausweisanlage}{\encl{Ausweiskopie}}
\newcommand{\bornlang}{\iflanguage{USenglish}{Born %(gebdat)s
(day.month.year) in %(gebort)s}{Geboren am %(gebdat)s in %(gebort)s}}
\newcommand{\country}{\iflanguage{ngerman}{\relax}{Germany}}

\setkomavar{fromname}{%(vorname)s %(nachname)s}
\setkomavar{fromaddress}{%(adresse)s\\%(plz)s %(ort)s}
%% Missbrauch der url-Variable: Wir wollen Geburtstag und Land nicht in der
%% backaddress haben
\setkomavar*{urlseparator}{}
\setkomavar{urlseparator}{}
\setkomavar{fromurl}{\bornlang\\\country}
\setkomavar{place}{%(ort)s}

\begin{document}
\selectlanguage{ngerman}
""")

# LETTERS ist ein Dictionary.  Der SchlÃ¼ssel dient dabei spÃ¤ter als
# SchlÃ¼ssel in den Checkboxen, der Wert ist ein Tripel aus einem
# Titel fÃ¼r die Checkbox, einer Einordnung (das sind die Ãœberschriften
# in der Briefauswahl, wobei noch durch einen SchrÃ¤gstrich eine
# Subkategorisierung vorgenommen werden kann) und dem Brieftext
# selbst (der sollte bei einer Erweiterung weiterhin das letzte
# Element sein, denn so lÃ¤uft makePdf oder Ã„nderung weiter).
# Ist der Brieftext leer, wird die Checkbox disabled und
# stattdessen auf eine FuÃŸnote verwiesen.
LETTERS = {
################### BKA
"bka": ("Bundeskriminalamt (4)", "Bund",
ur"""
\begin{letter}{Bundeskriminalamt\\
Der Datenschutzbeauftragte\\
65173 Wiesbaden
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir nach \S12, Abs. 5  Bundeskriminalamtgesetz  (BKAG),
\S10, Abs. 2 ATDG sowie
\S19, Abs. 1 Bundesdatenschutzgesetz (BDSG) Auskunft zu folgenden Punkten:


\begin{itemize}
\item Ã¼ber  die  durch  das   Bundeskriminalamt   zu
meiner   Person in  Systemen  der elektronischen  Datenerfassung  und
-verarbeitung gespeicherten Daten, im Besonderen Ã¼ber
personenbezogene DatensÃ¤tze im  polizeilichen  Informationssystem
(INPOL) sowie in am BKA gefÃ¼hrten gemeinsamen Dateien;

\item Ã¼ber den Zweck der Verarbeitung der Daten sowie Ã¼ber ihre
Herkunft;

\item Ã¼ber EmpfÃ¤nger oder  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt wurden, unter besonderer BerÃ¼cksichtigung von nach
Â§14 BKAG an Stellen im Ausland Ã¼bermittelter Daten.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),

################### BGS
"bgs": ("Bundespolizei (3)", "Bund",
ur"""
\begin{letter}{Beauftragter fÃ¼r den Datenschutz\\
der Bundespolizei\\
Heinrich-Mann-Allee 103\\
14473 Potsdam
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir nach 
\S19, Abs. 1 Bundesdatenschutzgesetz (BDSG) Auskunft zu folgenden Punkten:

\begin{itemize}
\item Ã¼ber  die  durch  die   Bundespolizei  zu   meiner   Person
in  Systemen  der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten Daten,
im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze im  Bundespolizeiaktennachweis (BAN)
sowie in Vorgangsverwaltungsanwendungen wie @rtus;

\item Ã¼ber den Zweck der Verarbeitung der Daten;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden,   unter   besonderer   BerÃ¼cksichtigung   einer
Ãœbermittlung    an    Polizeidienststellen,     an     Staatsanwaltschaften,
VerfassungsschutzbehÃ¶rden, den  Bundesnachrichtendienst,  den  militÃ¤rischen
Abschirmdienst und andere BehÃ¶rden  des  Bundesministers  der  Verteidigung
sowie BehÃ¶rden der Finanzverwaltung.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\ausweisanlage
\end{letter}
"""),

################### Zoll
"zka": ("Zoll", "Bund",
ur"""
\begin{letter}{Zollkriminalamt\\
Der behÃ¶rdliche Datenschutzbeauftragte\\
Postfach 850562\\
51030 KÃ¶ln
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir nach \S19, Abs.~1 Bundesdatenschutzgesetz (BDSG) Auskunft zu folgenden Punkten:


\begin{itemize}
\item Ã¼ber  die  durch  das   Zollkriminalamt  zu   meiner   Person
in Systemen  der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten Daten,   
im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze im Informationssystem des Zolls INZOLL;

\item Ã¼ber den Zweck der Verarbeitung der Daten;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist,

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden,   unter   besonderer   BerÃ¼cksichtigung   von
Ãœbermittlungen    an    Polizeidienststellen,     an     Staatsanwaltschaften,
VerfassungsschutzbehÃ¶rden, den  Bundesnachrichtendienst,  den  militÃ¤rischen
Abschirmdienst und andere BehÃ¶rden  des  Bundesministers  der  Verteidigung
sowie BehÃ¶rden der Finanzverwaltung.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),


################# Bundesamt VS will Grund
"bvs": (u"Bundesamt fÃ¼r Verfassungsschutz", "Bund",
None),

################# Generalbundeswanwalt (ZStV)
"zstv": ("Zentrales Verfahrensregister", "Bund",
ur"""
\begin{letter}{Bundesamt fÃ¼r Justiz\\
RegisterbehÃ¶rde\\
53094 Bonn
}

\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}


\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir nach \S249 StPO und Â§9 der Verordnung Ã¼ber den
Betrieb des Zentralen Staatsanwaltschaftlichen Verfahrensregisters, in
Verbindung mit \S19 BDSG, Auskunft Ã¼ber die zu meiner Person im
Zentralen Staatsanwaltschaftlichen Verfahrensregister (ZStV)
gespeicherten Daten.


\closing{}
\end{letter}
"""),


################# LKA BaWÃ¼
"lkabawu": (u"LKA Baden-WÃ¼rttemberg (3)", u"LÃ¤nder/Baden-WÃ¼rttemberg",
ur"""
\begin{letter}{Landeskriminalamt Baden-WÃ¼rttemberg\\
Taubenheimstrasse 85\\
70372 Stuttgart
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S45  Polizeigesetz  
Baden-WÃ¼rttemberg (PolG), \S11, Abs.~5 Verordnung  des  
Innenministeriums  Baden-WÃ¼rttemberg zur DurchfÃ¼hrung des Polizeigesetzes 
(DVO PolG),  \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG) und \S21, Abs.~1  Landesdatenschutzgesetz  (LDSG)
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Baden-WÃ¼rttemberg  zu
meiner  Person in   Systemen   der elektronischen  Datenerfassung  und
-verarbeitung gespeicherten  Daten,   im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze im polizeilichen Auskunftssystem POLAS sowie
im elektronischen Vorgangsbearbeitungssystemen, aber auch in
Hilfsdateien wie etwa der AD PMK;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder
sonst  bekannt ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\ausweisanlage
\end{letter}
"""),


############# VS BaWÃ¼ will Grund
"vsbw": (u"Verfassungsschutz Baden-WÃ¼rttemberg", u"LÃ¤nder/Baden-WÃ¼rttemberg",
	None),


############# VS Brandenburg
"vsbrabu": ("Verfassungsschutz Brandenburg", u"LÃ¤nder/Brandenburg",
ur"""
\begin{letter}{Ministerium des Inneren des Landes Brandenburg\\
Abteilung Verfassungsschutz\\
Postfach 60 11 26\\
14411 Potsdam
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S18  des Brandenburgischen 
Datenschutzgesetzes sowie \S12, Abs.~1 des Brandenburgischen 
Verfassungsschutzgesetzes Auskunft
Ã¼ber die durch Ihre BehÃ¶rde zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im   Besonderen   Ã¼ber 
personenbezogene DatensÃ¤tze, die der brandenburgische Verfassungsschutz in
NADIS pflegt.  Ebenfalls bitte ich Sie um Auskunft Ã¼ber die Herkunft der
Daten sowie Zweck und EmpfÃ¤nger von Ãœbermittlungen dieser Daten.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),


############# LKA Brandenburg
"lkabrabu": ("LKA Brandenburg", u"LÃ¤nder/Brandenburg",
ur"""
\begin{letter}{PolizeiprÃ¤sidium des Landes Brandenburg\\
Kaiser-Friedrich-StraÃŸe 143\\
14469 Potsdam
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S18  des Brandenburgischen 
Datenschutzgesetzes sowie \S71, Abs.~1 des Brandenburgischen 
Polizeigesetzes Auskunft
Ã¼ber die durch Ihre BehÃ¶rde zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im Besonderen zu DatensÃ¤tzen in den Datenbanksystemen PASS und ASS.
Ebenfalls bitte ich Sie um Auskunft Ã¼ber die Herkunft der
Daten sowie Zweck und EmpfÃ¤nger von Ãœbermittlungen dieser Daten.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),


################# Bayern VS will Grund
"vsby": ("Verfassungsschutz Bayern", u"LÃ¤nder/Bayern",
None),

"lkaby": ("LKA Bayern (3)", u"LÃ¤nder/Bayern",
ur"""
\begin{letter}{Landeskriminalamt Bayern\\
MaillingerstraÃŸe 15\\
80636 MÃ¼nchen
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von Artikel~48 des Gesetzes Ã¼ber die Aufgaben und Befugnisse der Bayerischen Staatlichen Polizei sowie \S19  Abs.~1
Bundesdatenschutzgesetz (BDSG) 
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch Ihre oder im Auftrag Ihrer BehÃ¶rde zu  meiner
Person in Systemen   der elektronischen  Datenerfassung  und
-verarbeitung gespeicherten  Daten.  Angesichts des jedenfalls von auÃŸen
nicht mehr zu durchblickenden Dickichts solcher Dateien im Bereich der
bayrischen Polizei bitte ich dabei um Sorgfalt bei der BerÃ¼cksichtigung
sÃ¤mtlicher Datenbanken, fÃ¼r die Sie die datenschutzrechtliche
Verantwortung tragen;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse aufgrund der vom
bayerischen Landesbeauftragen fÃ¼r Datenschutz regelmÃ¤ÃŸig gerÃ¼gten MissbrÃ¤uche
Ihrer BehÃ¶rde unter  Wahrnehmung meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten
Grundrechts  auf   informationelle Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

################# LKA Berlin
"lkaberlin": ("LKA Berlin (3)", u"LÃ¤nder/Berlin",
ur"""
\begin{letter}{Landeskriminalamt Berlin\\
Tempelhofer Damm 12\\
12101 Berlin-Tempelhof
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S16 Berliner Datenschutzgesetz
(soweit anwendbar) und \S50 Polizeigesetz Berlin
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Berlin  zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung
gespeicherten  Daten,   im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze in ISVB bzw.~POLIKS;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden;
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),

############# VS Berlin
"vsberlin": ("Verfassungsschutz Berlin (3)", u"LÃ¤nder/Berlin",
ur"""
\begin{letter}{Senatsverwaltung fÃ¼r Inneres\\
Abteilung II -- Verfassungsschutz\\
Postfach 62 05 60\\
10795 Berlin
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir nach \S31, Abs.~1 des Gesetzes Ã¼ber den Verfassungsschutz
in Berlin
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landesamt fÃ¼r Verfassungsschutz Berlin
zu  meiner  Person  in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung
gespeicherten  Daten,   im   Besonderen   Ã¼ber
von Ihrer BehÃ¶rde in NADIS eingespeiste Daten zu meiner Person.  
Soweit diese nicht Ihrer
alleinigen VerfÃ¼gungsberechtigung unterliegen, bitte ich um Mitteilung, welche
Stelle auskunftsbefugt ist;

\item Ã¼ber den Zweck und die Rechtsgrundlage der Speicherung und Verarbeitung.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\ausweisanlage
\end{letter}
"""),

############# VS Bremen
"vsbremen": ("Verfassungsschutz Bremen(1)", u"LÃ¤nder/Bremen",
ur"""
\begin{letter}{Landesamt fÃ¼r Verfassungsschutz Bremen\\
Flughafenallee 23\\
28199 Bremen\\
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir auf Grundlage  von \S19, Abs.~1
Bundesdatenschutzgesetz (BDSG) sowie \S4, Abs.~1 des Bremischen
Datenschutzgesetzes (BremDSG) Auskunft Ã¼ber die durch Ihre
BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) zu meiner Person
in Systemen der elektronischen Datenerfassung und \hbox{-verarbeitung}
gespeicherten Daten, im Besonderen Ã¼ber personenbezogene DatensÃ¤tze,
die das Landesamt fÃ¼r Verfassungsschutz Bremen in NADIS pflegt, den
Zweck der Speicherung sowie, soweit mÃ¶glich, die Herkunft der Daten und
im Fall einer Ãœbermittlung deren EmpfÃ¤nger.

Meiner Anfrage liegt ein generelles Informationsinteresse unter Wahrnehmung
meines verfassungsrechtlich ver\-bÃ¼rg\-ten Grundrechts auf informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

############# Polizei Bremen
"lkabremen": ("LKA Bremen", u"LÃ¤nder/Bremen",
ur"""
\begin{letter}{Polizei Bremen\\
Kriminalpolizei/LKA\\
In der Vahr 76\\
28329 Bremen
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir auf Grundlage von \S4, Abs.~1 des Bremischen
Datenschutzgesetzes (BremDSG)) zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Bremen zu meiner Person
in Systemen der
elektronischen Datenerfassung  und  -verarbeitung 
gespeicherten Daten, im Besonderen Ã¼ber
personenbezogene DatensÃ¤tze in Poliks sowie der polizeilichen
Vorgangsverwaltung;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese gespeichert oder
sonst bekannt ist;

\item Ã¼ber die EmpfÃ¤nger oder die Gruppen von EmpfÃ¤ngern, an die die
Daten Ã¼bermittelt wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter Wahrnehmung
meines verfassungsrechtlich ver\-bÃ¼rg\-ten Grundrechts auf informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

############# VS Hamburg
"vshamburg": ("Verfassungsschutz Hamburg", u"LÃ¤nder/Hamburg",
ur"""
\begin{letter}{Hamburger Landesamt fÃ¼r Verfassungsschutz\\
Johanniswall 4\\
20095 Hamburg
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir auf Grundlage  von \S19 Abs.~1
Bundesdatenschutzgesetz (BDSG) sowie \S23, Abs.~1 des Hamburgischen 
Verfassungsschutzgesetzes (HmbVerfSchG) Auskunft Ã¼ber die durch Ihre
BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) zu meiner Person
in Systemen der elektronischen Datenerfassung und -verarbeitung
gespeicherten Daten, im Besonderen Ã¼ber personenbezogene DatensÃ¤tze,
die der Hamburgische Verfassungsschutz in NADIS pflegt, den
Zweck der Speicherung sowie, soweit mÃ¶glich, die Herkunft der Daten und
im Fall einer Ãœbermittlung deren EmpfÃ¤nger.

Meiner Anfrage liegt ein generelles Informationsinteresse unter Wahrnehmung
meines verfassungsrechtlich ver\-bÃ¼rg\-ten Grundrechts auf informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

############# Polizei Hamburg
"lkahamburg": ("LKA Hamburg", u"LÃ¤nder/Hamburg",
ur"""
\begin{letter}{Polizei Hamburg\\
Bruno-Georges-Platz 1\\
22297 Hamburg
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir auf Grundlage von \S18 Abs.~1 des Hamburgischen
Datenschutzgesetzes (HmbDSG) zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Hamburg zu meiner Person
in Systemen der
elektronischen Datenerfassung  und  -verarbeitung
gespeicherten Daten, im Besonderen Ã¼ber
personenbezogene DatensÃ¤tze in POLAS sowie in der polizeilichen
Vorgangsverwaltung ComVor;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese gespeichert oder
sonst bekannt ist;

\item Ã¼ber die EmpfÃ¤nger oder die Gruppen von EmpfÃ¤ngern, an die die
Daten Ã¼bermittelt wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter Wahrnehmung
meines verfassungsrechtlich ver\-bÃ¼rg\-ten Grundrechts auf informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),


############# LKA Hessen
"lkahessen": ("LKA Hessen", u"LÃ¤nder/Hessen",
ur"""
\begin{letter}{Landeskriminalamt Hessen\\
HÃ¶lderlinstraÃŸe 5\\
65187 Wiesbaden
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir nach \S29 des hessischen Gesetzes Ã¼ber die Ã¶ffentliche
Sicherheit und Ordnung
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Hessen  zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung
gespeicherten  Daten,   im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze im polizeilichen Auskunftssystem POLAS-HE sowie
der Vorgangsverwaltung ComVor;

\item Ã¼ber den Zweck und die Rechtsgrundlage der Speicherung und Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),

############# VS Hessen
"vshessen": ("Verfassungsschutz Hessen", u"LÃ¤nder/Hessen",
ur"""
\begin{letter}{Landesamt fÃ¼r Verfassungsschutz Hessen\\
Postfach 39 05\\
65029 Wiesbaden
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir nach \S18, Abs.~1 des Hessischen Gesetzes Ã¼ber das
Landesamt fÃ¼r Verfassungsschutz
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landesamt fÃ¼r Verfassungsschutz Hessen  zu
meiner  Person in   Systemen   der elektronischen  Datenerfassung  und
-verarbeitung gespeicherten  Daten,   im   Besonderen   Ã¼ber durch von
Ihrer BehÃ¶rde zu meiner Person in NADIS eingespeiste Daten;

\item Ã¼ber den Zweck und die Rechtsgrundlage der Speicherung und Verarbeitung.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

Sofern die Auskunft nach \S18, Abs.~2 unterbleibt, bitte ich Sie um 
diesbezÃ¼gliche Unterrichtung.

\closing{}
\end{letter}
"""),

############# VS Meckvop
"vsmv": ("Verfassungsschutz Mecklenburg-Vorpommern",
u"LÃ¤nder/Mecklenburg-Vorpommern",
ur"""
\begin{letter}{Innenministerium Mecklenburg-Vorpommern\\
Verfassungsschutz\\
Postfach 11 05 52\\
19005 Schwerin
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von   \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG) und \S26, Abs.~1 des Gesetzes Ã¼ber den
Verfassungsschutz im Lande Mecklenburg-Vorpommern
Auskunft
Ã¼ber die durch Ihre BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) 
zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im   Besonderen   Ã¼ber 
personenbezogene DatensÃ¤tze, die der Verfassungsschutz
Mecklenburg-Vorpommern
zu meiner Person in NADIS pflegt, den Zweck und ggf.~die
Rechtsgrundlage der Speicherung sowie eventuelle EmpfÃ¤nger der Daten.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),


################# LKA Meckvop
"lkamv": ("LKA Mecklenburg-Vorpommern (3)", u"LÃ¤nder/Mecklenburg-Vorpommern",
ur"""
\begin{letter}{Landeskriminalamt Mecklenburg-Vorpommern\\
Retgendorfer Str. 2\\
19067 Rampe
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von   \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG) und \S48, Abs.~1 Gesetz Ã¼ber die
Ã¶ffentliche Sicherheit und Ordnung in Mecklenburg-Vorpommern Auskunft
\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Mecklenburg-Vorpommern  
zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,   im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze in der Polizeilichen Erkenntnisdatei
PED bzw.~in Ihrer Vorgangsverwaltung;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\ausweisanlage
\end{letter}
"""),


############# VS Niedersachsen
"vsnds": ("Verfassungsschutz Niedersachsen", u"LÃ¤nder/Niedersachsen",
ur"""
\begin{letter}{NiedersÃ¤chsisches Ministerium fÃ¼r Inneres, Sport und Integration\\
BÃ¼ttnerstraÃŸe 28\\
30165 Hannover
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von   \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG) sowie \S13, Abs.~1 des Gesetzes Ã¼ber den
Verfassungsschutz im Lande Niedersachsen
Auskunft
Ã¼ber die durch Ihre BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) 
zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im   Besonderen   Ã¼ber 
personenbezogene DatensÃ¤tze, die der NiedersÃ¤chsische Verfassungsschutz 
zu meiner Person in NADIS pflegt, den
Zweck der Speicherung sowie, soweit mÃ¶glich, die Herkunft der Daten und
im Fall einer Ãœbermittlung deren EmpfÃ¤nger.


Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),


################# LKA Niedersachsen
"lkasaar": ("LKA Niedersachsen", u"LÃ¤nder/Niedersachsen",
ur"""
\begin{letter}{LKA Niedersachsen\\
SchÃ¼tzenstraÃŸe 25\\
30161 Hannover
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S16, Abs.~1 des
NiedersÃ¤chsischen Datenschutzgesetzes
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Niedersachsen  zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,   im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze in POLAS und in der Vorgangsverwaltung
NIVADIS;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

############# VS NRW
"vsnrw": ("Verfassungsschutz Nordrhein-Westfalen",
u"LÃ¤nder/Nordrhein-Westfalen",
ur"""
\begin{letter}{Innenministerium des Landes Nordrhein-Westfalen\\
Abteilung Verfassungsschutz\\
HaroldstraÃŸe 5\\
40213 DÃ¼sseldorf
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von   \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG), \S5, Abs.~1 und \S18 Datenschutzgesetz
Nordrhein-Westfalen, sowie \S14, Abs.~1 des Gesetzes Ã¼ber den
Verfassungsschutz in Nordrhein-Westfalen
Auskunft
Ã¼ber die durch Ihre BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) 
zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im   Besonderen   Ã¼ber 
personenbezogene DatensÃ¤tze, die der Verfassungsschutz
Nordrhein-Westfalen
zu meiner Person in NADIS pflegt, sowie den Zweck und ggf.~die
Rechtsgrundlage der Speicherung.

Soweit meine Daten in Akten gespeichert sind, bitte ich gemÃ¤ÃŸ Â§18 Abs.~2
Datenschutzgesetz Nordrhein-Westfalen um Akteneinsicht.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),


################# LKA NRW
"lkanrw": ("LKA Nordrhein-Westfalen (3)", u"LÃ¤nder/Nordrhein-Westfalen",
ur"""
\begin{letter}{Landeskriminalamt Nordrhein-Westfalen\\
VÃ¶lklinger Str. 49\\
40221 DÃ¼sseldorf
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir  auf  Grundlage  von   \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG), \S5, Abs.~1 und \S18 Datenschutzgesetz
Nordrhein-Westfalen Auskunft
\begin{itemize}
\item Ã¼ber die von den PolizeibehÃ¶rden des Landes Nordrhein-Westfalen zu 
meiner Person in Systemen der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,   im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze in POLAS bzw.~in der Vorgangsverwaltung IGVP;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\ausweisanlage
\end{letter}
"""),


############# VS RP
"vsrp": ("Verfassungsschutz Rheinland-Pfalz", u"LÃ¤nder/Rheinland-Pfalz",
ur"""
\begin{letter}{Ministerium des Inneren und fÃ¼r Sport des Landes Rheinland-Pfalz\\
Abteilung Verfassungsschutz\\
Postfach 32 80\\
55022 Mainz
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von   \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG) sowie \S18, Abs.~1 des Landesverfassungsschutzgesetzes Rheinland-Pfalz
Auskunft
Ã¼ber die durch Ihre BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) 
zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im   Besonderen   Ã¼ber 
personenbezogenen DatensÃ¤tze, die der Verfassungsschutz Rheinland-Pfalz 
zu meiner Person in NADIS pflegt, den
Zweck der Speicherung sowie, soweit mÃ¶glich, die Herkunft der Daten und
im Fall einer Ãœbermittlung deren EmpfÃ¤nger.


Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),


################# LKA RP
"lkarp": ("LKA Rheinland-Pfalz (3)", u"LÃ¤nder/Rheinland-Pfalz",
ur"""
\begin{letter}{Landeskriminalamt Rheinland-Pfalz\\
Valenciaplatz 1-7\\
55118 Mainz
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S40, Abs.~1 Polizei- und OrdnungsbehÃ¶rdengesetz
Rheinland-Pfalz (POG),  \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG) und \S18 Abs.~1 und 3  Landesdatenschutzgesetz  (LDSG)
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Rheinland-Pfalz  zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung
gespeicherten  Daten,   im   Besonderen   Ã¼ber
personenbezogene DatensÃ¤tze in RIVAR;

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.

\item Ã¼ber den strukturierten Ablauf der automatisierten  Verarbeitung  der  meine
Person betreffenden Daten.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\ausweisanlage
\end{letter}
"""),


############# VS Saarland
"vssaar": ("Verfassungsschutz Saarland", u"LÃ¤nder/Saarland",
ur"""
\begin{letter}{Landesamt fÃ¼r Verfassungsschutz Saarland\\
Postfach 10 20 63\\
66020 SaarbrÃ¼cken
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von   \S19,  Abs.~1
Bundesdatenschutzgesetz (BDSG) sowie \S21, Abs.~1 des SaarlÃ¤ndischen
Verfassungsschutzgesetzes
Auskunft
Ã¼ber die durch Ihre BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) 
zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im   Besonderen   Ã¼ber 
personenbezogene DatensÃ¤tze, die das Landesamt fÃ¼r Verfassungsschutz 
Saarland zu meiner Person in NADIS pflegt, sowie nach MÃ¶glichkeit Ã¼ber die
Herkunft und EmpfÃ¤nger eventueller Ãœbermittlungen der Daten.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde. 

\closing{}
\end{letter}
"""),


################# LKA Saarland
"lkands": ("LKA Saarland", u"LÃ¤nder/Saarland",
ur"""
\begin{letter}{Landeskriminalamt Saarland\\
HellwigstraÃŸe 14\\
66121 SaarbrÃ¼cken
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S19 und \S20, Abs.~1
des SaarlÃ¤ndischen Gesetzes zum Schutz personenbezogener Daten
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Saarland  zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung und  -verarbeitung (auch im Wege der
Auftragsdatenspeicherung)   gespeicherten  Daten,   

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),


############# VS Sachsen
"vssachsen": (u"Landesamt fÃ¼r Verfassungsschutz Sachsen", u"LÃ¤nder/Sachsen",
ur"""
\begin{letter}{Landesamt fÃ¼r Verfassungsschutz Sachsen\\
Postfach 10 02 47\\
01072 Dresden
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S18, Abs.~1  des SÃ¤chsischen 
Datenschutzgesetzes sowie \S9, Abs.~1 des SÃ¤chsischen Verfassungsschutzgesetzes
Auskunft
Ã¼ber die durch Ihre BehÃ¶rde (auch im Weg der Auftragsdatenverarbeitung) 
zu meiner Person in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung gespeicherten  Daten,
im   Besonderen   Ã¼ber 
personenbezogenen DatensÃ¤tze, die der sÃ¤chsische Verfassungsschutz in
NADIS pflegt, den
Zweck der Speicherung sowie, soweit mÃ¶glich, die Herkunft der Daten und
im Fall einer Ãœbermittlung deren EmpfÃ¤nger.


Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

############# LKA Sachsen
"lkasachsen": ("LKA Sachsen", u"LÃ¤nder/Sachsen",
ur"""
\begin{letter}{Landeskriminalamt Sachsen\\
NeulÃ¤nder StraÃŸe 60\\
01129 Dresden
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S18  des SÃ¤chsischen 
Datenschutzgesetzes sowie \S51 des SÃ¤chsischen Polizeigesetzes
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch das Landeskriminalamt Sachsen  zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung
gespeicherten  Daten,   im   Besonderen   Ã¼ber die
personenbezogenen DatensÃ¤tze in der Datenbank 
IVO (Integrierte Vorgangsbearbeitung);

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist. Sofern eine solche Auskunft unter Berufung auf \S51 SÃ¤chsPolG unterbleibt,
bitte ich um Mitteilung darÃ¼ber;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),


############# VS Sachsen-Anhalt
"vssa": ("VS Sachsen-Anhalt (3)", u"LÃ¤nder/Sachsen-Anhalt",
ur"""
\begin{letter}{Verfassungsschutz in Sachsen-Anhalt\\
Ministerium des Innern des Landes Sachsen-Anhalt\\
Abteilung 5\\
Postfach 18 49\\
39008 Magdeburg
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von \S15
Landesdatenschutzgesetz Sachsen-Anhalt sowie \S14 des Gesetzes Ã¼ber den
Verfassungsschutz in Sachsen-Anhalt
Auskunft Ã¼ber die von Ihrer BehÃ¶rde (auch im Wege
der Auftragsdatenverarbeitung etwa in NADIS) zu meiner Person
in System zur elektronischen Datenverarbeitung gespeicherten Daten, den
Zweck der Speicherung sowie, soweit mÃ¶glich, die Herkunft der Daten und
im Fall einer Ãœbermittlung deren EmpfÃ¤nger.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\ausweisanlage
\end{letter}
"""),


############# LKA Sachsen-Anhalt
"lkasa": ("LKA Sachsen-Anhalt (3)", u"LÃ¤nder/Sachsen-Anhalt",
ur"""
\begin{letter}{Landeskriminalamt Sachsen-Anhalt\\
LÃ¼becker StraÃŸe 53-63\\
39124 Magdeburg
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S15
Landesdatenschutzgesetz Sachsen-Anhalt 
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch Ihre BehÃ¶rde sowie Ihnen nachgeordnete BehÃ¶rden
zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung, im Besonderen in der
Vorgangsbearbeitung Ivopol oder in DITRALIS, 
gespeicherten Daten;

\item Ã¼ber den Zweck und die Rechtsgrundlage der Verarbeitung und
Speicherung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist; 

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\ausweisanlage
\end{letter}
"""),



############# LKA Schleswig-Holstein
"lkash": ("LKA Schleswig-Holstein (3)", u"LÃ¤nder/Schleswig-Holstein",
ur"""
\begin{letter}{Landeskriminalamt Schleswig-Holstein\\
MÃ¼hlenweg 166, Haus 12\\
24116 Kiel
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S27  des 
Landesdatenschutzgesetzes Schleswig-Holstein sowie \S198 des Allgemeinen
Verwaltungsgesetzes fÃ¼r das Land Schleswig-Holstein
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch Ihre BehÃ¶rde sowie Ihnen nachgeordnete BehÃ¶rden
zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  -verarbeitung, im Besonderen in
INPOL-Land sowie Vorgangsbearbeitungsanwendungen gespeicherten Daten;

\item Ã¼ber den Zweck und die Rechtsgrundlage der Verarbeitung und
Speicherung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist; 

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\ausweisanlage
\end{letter}
"""),


############# VS Schleswig-Holstein
"vssh": ("VS Schleswig-Holstein", u"LÃ¤nder/Schleswig-Holstein",
ur"""
\begin{letter}{Innenministerium des Landes Schleswig-Holstein\\
Abt. IV 7 - Verfassungsschutz\\
Postfach 71 25\\
24171 Kiel
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S27  des 
Landesdatenschutzgesetzes Schleswig-Holstein sowie \S25 des 
Landesverfassungsschutzgesetzes Schleswig-Holstein
Auskunft Ã¼ber die von Ihrer BehÃ¶rde (auch im Wege
der Auftragsdatenverarbeitung etwa in NADIS) zu meiner Person
in System zur elektronischen Datenverarbeitung gespeicherten Daten,  den
Zweck der Speicherung sowie, soweit mÃ¶glich, die Herkunft der Daten und
im Fall einer Ãœbermittlung deren EmpfÃ¤nger.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

############# LKA ThÃ¼ringen
"lkathuer": (u"LKA ThÃ¼ringen", u"LÃ¤nder/ThÃ¼ringen",
ur"""
\begin{letter}{ThÃ¼ringer Landeskriminalamt\\
Postfach 10 18 27\\
99018 Erfurt
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf  Grundlage  von  \S13  des ThÃ¼ringer 
Datenschutzgesetzes sowie \S47 des ThÃ¼ringischen Polizeigesetzes
zu folgenden Punkten Auskunft:

\begin{itemize}
\item Ã¼ber die durch Ihre BehÃ¶rde zu  meiner  Person
in   Systemen   der
elektronischen  Datenerfassung  und  \hbox{-verarbeitung}
gespeicherten  Daten, im Besonderen auch Ã¼ber in Datenbanken zur
Vorgangsbearbeitung wie IGVP vorgehaltene Daten; 

\item Ã¼ber den Zweck der Verarbeitung;

\item Ã¼ber die Herkunft der Daten, soweit diese  gespeichert  oder  sonst  bekannt
ist; 

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  die  Daten
Ã¼bermittelt  wurden.
\end{itemize}
Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

Vorsorglich weise ich darauf hin, dass ich dies als hinreichend  im
Hinblick auf Â§47 (1) ThÃ¼rPAG ansehe.  Da mir kaum stichhaltigere GrÃ¼nde
fÃ¼r ein Auskunftsverlangens einfallen als eben die Wahrnehmung eines
Grundrechts, werde ich keine weiteren GrÃ¼nde angeben.

\closing{}
\end{letter}
"""),


############# VS ThÃ¼ringen
"vsthuer": (u"Verfassungsschutz ThÃ¼ringen", u"LÃ¤nder/ThÃ¼ringen",
None),


############ Sirene
"sisde": (u"SIS, PrÃ¼m, Europol (2,4)", u"International/EU-BRD",
ur"""
\begin{letter}{Bundeskriminalamt\\
Datenschutzbeauftragter\\
65173 Wiesbaden
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie mir auf Grundlage von Artikel 109 des Schengener
DurchfÃ¼hrungsabkommens in Ihrer Eigenschaft als nationaler
SIRENE-Kontakt Auskunft Ã¼ber zu  meiner  Person im \textbf{Schengen-Informationssystem}
gespeicherte  Daten, die  die Herkunft dieser Daten sowie
EmpfÃ¤nger oder  Gruppen  von  EmpfÃ¤ngern,  an  die  
die  Daten Ã¼bermittelt wurden bzw.~von denen sie abgefragt wurden;

Weiter bitte ich Sie, mir auf Grundlage  von Artikel~40 PrÃ¼merVtrG i.V.m.~Art.
31 Abs.~1 des Beschlusses 2008/615/JI des Rates der EuropÃ¤ischen Union
Auskunft zu erteilen Ã¼ber die im Rahmen der Bestimmungen des
\textbf{PrÃ¼mer Vertrags} durch das BKA zu meiner Person verarbeiteten
Daten, deren Herkunft, EmpfÃ¤nger oder EmpfÃ¤ngerkategorien von
Ãœbertragungen, den dabei vorgesehenen Verarbeitungszweck sowie die
jeweilige Rechtsgrundlage der Verarbeitung.  Sofern eine andere
Abteilung des BKA fÃ¼r PrÃ¼m-AuskÃ¼nfte zustÃ¤ndig ist, bitte ich um
entsprechende Veranlassung.

SchlieÃŸlich bitte ich auf Grundlage von Artikel 30 des Ratsbeschlusses
2009/371/JHA i.V.m.~Â§2 EuropolG um Auskunft Ã¼ber Daten, die zu
meiner Person bei \textbf{Europol} gespeichert und/oder verarbeitet werden.

Meiner Anfrage liegt ein generelles Informationsinteresse unter  Wahrnehmung
meines  verfassungsrechtlich  ver\-bÃ¼rg\-ten  Grundrechts  auf   informationelle
Selbstbestimmung zugrunde.

\closing{}
\end{letter}
"""),

"sisat": (u"SIS,PrÃ¼m (2)", u"International/EU-Ã–sterreich",
ur"""
\begin{letter}{Bundesministerium fÃ¼r Inneres (BMI)\\
Bundeskriminalamt, SIRENE Ã–sterreich\\
Josef Holaubek Platz 1\\
1090 Wien
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf Grundlage von Artikel 109 des Schengener
DurchfÃ¼hrungsabkommens Auskunft:

\begin{itemize}
\item Ã¼ber zu  meiner  Person im Schengen-Informationssystem
gespeicherte  Daten;

\item Ã¼ber die Herkunft dieser Daten,;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  
die  Daten Ã¼bermittelt wurden bzw.~von denen sie abgefragt wurden,
soweit die entsprechenden Protokolle noch verfÃ¼gbar sind.
\end{itemize}
Weiter bitte ich Sie, mir auf der Grundlage von Art.~40 des
sog.~Vertrages von PrÃ¼m Auskunft zu erteilen Ã¼ber die im Rahmen der
Vertragsbestimmungen durch das BKA zu meiner Person

\begin{itemize}
\item verarbeiteten Daten, 
\item deren Herkunft, 
\item EmpfÃ¤nger oder EmpfÃ¤ngerkategorien von Ãœbertragungen, 
\item den dabei vorgesehenen Verarbeitungszweck sowie 
\item die Rechtsgrundlage der Verarbeitung.
\end{itemize}

\closing{}
\end{letter}
"""),

"sisch": ("SIS (2,3)", u"International/EU-Schweiz",
ur"""
\begin{letter}{Bundesamt fÃ¼r Polizei\\
Datenschutzberaterin oder SIRENE-BÃ¼ro\\
Nussbaumstrasse 29\\
3003 Bern
}
\setkomavar{subject}{Auskunft Ã¼ber zu meiner Person gespeicherte Daten}

\opening{Sehr geehrte Damen und Herren,}

bitte erteilen Sie  mir  auf Grundlage von Artikel 109 des Schengener
DurchfÃ¼hrungsabkommens Auskunft:

\begin{itemize}
\item Ã¼ber zu  meiner  Person im Schengen-Informationssystem
gespeicherte  Daten;

\item Ã¼ber die Herkunft dieser Daten,;

\item Ã¼ber die EmpfÃ¤nger oder  die  Gruppen  von  EmpfÃ¤ngern,  an  die  
die  Daten Ã¼bermittelt wurden bzw.~von denen sie abgefragt wurden,
soweit die entsprechenden Protokolle noch verfÃ¼gbar sind.
\end{itemize}

\closing{}
\ausweisanlage
\end{letter}
"""),

"usdhs": ("US DHS", u"International/USA",
ur"""
\selectlanguage{USenglish}
\begin{letter}{
Chief Privacy Officer/Chief FOIA Officer\\
U.S. Department of Homeland Security\\
245 Murray Drive SW, Building 410\\
STOP-0655\\
Washington, D.C. 20528-0655\\
USA
}
\setkomavar{subject}{Privacy/FOI Act Request}

\opening{Dear FOI Officer,}

This letter constitutes a request under the Privacy Act, 5 U.S.C. \S552a.

I request copies of all information pertaining to myself contained in
data processing systems operated by your agency, including, 
but not limited to, any Passenger Name Record (PNR) data and 
Interagency Border Inspection System (IBIS) data.	

If the volume of the information disclosed exceeds the limit below which
fees are waived, please contact me before such expenses are
incurred. 

If you deny all or any part of this request, please cite each specific
exemption that forms the basis of your refusal to release the
information and notify me of the appeal procedures available under the
law.

\closing{}
\end{letter}
\selectlanguage{ngerman}
"""),

###### Interpol
"interpol": ("Interpol (3)" , u"International/Interpol", 
ur"""
\selectlanguage{USenglish}
\begin{letter}{
Commission de Controle des Fichiers de l'O.I.P.C.-Interpol\\
200 Quai Charles de Gaulle\\
69006 Lyon\\
FRANCE
}

\setkomavar{subject}{Request for Access to Interpol's Databases}

\opening{Dear CCF officer,}

This letter constitutes a request for access to information 
as laid out in Article~9 of the Rules on the
Control of Information and Access to Interpol's Files.

I request copies of all information pertaining to myself contained in
data processing systems operated by Interpol.

\closing{With best regards,}
\encl{Proof of identity}
\end{letter}
\selectlanguage{ngerman}
"""),

########### Ã–sterreich

# LÃ¤nder sind programmatisch unten

'autfed': ("Innenministerium (3,6)", u"Ã–sterreich/Bund", ur"""
\begin{letter}{
Bundesministerium fÃ¼r Inneres (BMI)\\
Herrengasse 7\\
A-1014 Wien
}

\setkomavar{subject}{Auskunft gemÃ¤ÃŸ Datenschutzgesetz 2000}

\opening{Sehr geehrte Damen und Herren,}

GemÃ¤ÃŸ Â§\thinspace1 und 26 Datenschutzgesetz 2000 ersuche ich Sie um
Auskunft Ã¼ber die vom Bundesministerium des Inneren oder in seinem
Auftrag Ã¼ber mich innerhalb von Datenanwendungen gespeicherten Daten, im
Speziellen Ã¼ber

\begin{itemize}
\item die Art und Herkunft der Daten,
\item den Zweck der Datenspeicherung,
\item ihren Inhalt,
\item eventuelle Ãœbermittlungen und deren EmpfÃ¤nger sowie
\item die Rechtsgrundlage der Erfassung, Speicherung, und Verwendung.
\end{itemize}

Sollten Daten einem Dienstleister gemÃ¤ÃŸ Â§\thinspace10 DSG 2000 Ã¼berlassen
worden sein, so ersuche ich um die Bekanntgabe des Namens und der
Anschrift dieses Dienstleisters.

\closing{Mit freundlichen GrÃ¼ÃŸen,}

\encl{IdentitÃ¤tsnachweis}
\end{letter}
"""),
}


def addAutCountries():
# Ã–sterreich-SD ist alles ziemlich analog
	for shortId, longId, address in [
		('autbgl', u"Sicherheitsdirektion Burgenland",
			ur"Sicherheitsdirektion Burgenland\\Neusiedler StraÃŸe 84"
			ur"\\A-7001 Eisenstadt"),
		('autktn', u"Sicherheitsdirektion KÃ¤rnten",
			ur"Sicherheitsdirektion KÃ¤rnten\\Buchengasse 3\\A-9020 Klagenfurt"),
		('autnoe', u"Sicherheitsdirektion NiederÃ¶sterreich",
			ur"Sicherheitsdirektion NiederÃ¶sterreich\\Neue Herrengasse 15"
			ur"\\A-3100 St. PÃ¶lten"),
		('autooe', u"Sicherheitsdirektion OberÃ¶sterreich",
			ur"Sicherheitsdirektion OberÃ¶sterreich\\NietzschestraÃŸe 33"
			ur"\\A-4021 Linz"),
		('autsbg', u"Sicherheitsdirektion Salzburg",
			ur"Sicherheitsdirektion Salzburg\\AlpenstraÃŸe 90\\A-5020 Salzburg"),
		('autsmk', u"Sicherheitsdirektion Steiermark",
			ur"Sicherheitsdirektion Steiermark\\Parkring 10\\A-8010 Graz"),
		('auttir', u"Sicherheitsdirektion Tirol",
			ur"Sicherheitsdirektion Tirol\\Maria-Theresien-StraÃŸe 43"
			ur"\\A-6021 Innsbruck"),
		('autvrl', u"Sicherheitsdirektion Vorarlberg",
			ur"Sicherheitsdirektion Vorarlberg\\BahnhofstraÃŸe 45"
			ur"\\A-6900 Bregenz"),
		('autwie', u"Bundespolizeidirektion Wien",
			ur"Bundespolizeidirektion Wien\\Schottenring 7-9\\A-1010 Wien"),
	]:
		LETTERS[shortId] = ("%s (3,6)"%longId , u"Ã–sterreich/LÃ¤nder", 
ur"""
\begin{letter}{
%s
}

\setkomavar{subject}{Auskunft gemÃ¤ÃŸ Datenschutzgesetz 2000}

\opening{Sehr geehrte Damen und Herren,}

GemÃ¤ÃŸ Â§\thinspace1 und 26 Datenschutzgesetz 2000 ersuche ich Sie um Auskunft
Ã¼ber die von der %s Ã¼ber mich innerhalb von Datenanwendungen
gespeicherten Daten, im Speziellen Ã¼ber

\begin{itemize}
\item die Art und Herkunft der Daten,
\item den Zweck der Datenspeicherung,
\item ihren Inhalt,
\item eventuelle Ãœbermittlungen und deren EmpfÃ¤nger sowie
\item die Rechtsgrundlage der Erfassung, Speicherung, und Verwendung.
\end{itemize}

Sollten Daten einem Dienstleister gemÃ¤ÃŸ Â§\thinspace10 DSG 2000 Ã¼berlassen
worden sein, so ersuche ich um die Bekanntgabe des Namens und der
Anschrift dieses Dienstleisters.

\closing{Mit freundlichen GrÃ¼ÃŸen,}

\encl{IdentitÃ¤tsnachweis}
\end{letter}
"""%(address, longId))


def addScoringAgencies():
# Das sind Auskunfteien nach http://www.bfdi.bund.de/DE/Oeffentlichkeitsarbeit/Pressemitteilungen/2010/15_NovelleAuskunfteien.html
# Die gehen alle ziemlich gleich.
	for shortId, longId, address in [
		('schufa', "Schufa (6,7)",
			r"SCHUFA Holding AG\\Verbraucherservicezentrum Hannover\\"
			r"Postfach 56 40\\30056 Hannover"),
		('accumio', "accumio finance (6,7)",
			r"accumio finance services GmbH\\Customer Care Service Center"
			r"\\Postfach 110254\\30099 Hannover"),
		('arvato', "arvato infoscore (6,7)",
			ur"infoscore Consumer Data GmbH\\Abteilung Datenschutz"
			ur"\\RheinstraÃŸe 99\\76532 Baden-Baden"),
		('buergel', u"BÃ¼rgel (3,6,7)",
			ur"BÃ¼rgel Wirtschaftsinformationen GmbH & Co. KG"
			ur"\\z. Hd. Betrieblicher Datenschutzbeauftragter\\GasstraÃŸe 18"
			ur"\\22761 Hamburg"),
		('creditreform', "Creditreform (6,7)",
			r"CEG Creditreform Consumer GmbH\\Konsumentenservice"
			r"\\Hellersbergstr. 11\\41460 Neuss"),
		('deltavista', "Deltavista (6,7)",
			ur"Deltavista GmbH\\Datenschutz\\KaiserstraÃŸe 217\\76133 Karlsruhe"),
	]:
		LETTERS[shortId] = (longId , "Private/Scoringagenturen", 
ur"""
\begin{letter}{
%s
}

\setkomavar{subject}{Antrag auf Auskunftserteilung nach Â§ 34
Bundesdatenschutzgesetz (BDSG)}

\opening{Sehr geehrte Damen und Herren,}

hiermit bitte ich Sie, mir schriftlich zu folgenden Punkten 
Auskunft zu erteilen:

\begin{itemize}
\item Die bei Ihnen Ã¼ber mich gespeicherten personenbezogenen Daten,
\item die Herkunft meiner Daten,
\item den oder die EmpfÃ¤nger (bitte mit Namen und Adresse), an die Sie meine Daten
      Ã¼bermittelt haben,
\item meine aktuellen Wahrscheinlichkeitswerte (Scorewerte) und die zu meiner Person
      innerhalb der letzten zwÃ¶lf Monate Ã¼bermittelten Scorewerte,
\item eine individuelle und einzelfallbezogene ErklÃ¤rung meiner Scorewerte.
\end{itemize}

\closing{Mit freundlichen GrÃ¼ÃŸen,}
\end{letter}
"""%address)

addAutCountries()
addScoringAgencies()


######################## Web-Interface

def parseRemarks(title):
	"""returns a "real" title and HTML for a title with remarks.

	Remarks are comma-seperated numbers in parentheses.  They are turned
	into footnotes going to rem<number> anchors.
	"""
	mat = re.match(r"(.*)\s*\(([\d,\s]*)\)", title)
	if not mat:
		return title, ""
	else:
		return (
			mat.group(1), 
			"<sup>%s</sup>"%(",".join([
				"<a href='#rem%s'>%s</a>"%(s.strip(),s.strip())
					for s in mat.group(2).split(",")])))


def _getLetterDict(letters=LETTERS):
	"""gibt ein Dict {Ãœberschrift:{UnterÃ¼berschrift:(desc, key, text)}} zurÃ¼ck.

	desc und key sind eine Kurzbeschreibung und der AuswahlschlÃ¼ssel
	eines Briefs.

	Dies ist ein Helfer fÃ¼r getLetterMenu.
	"""
	lettersDict = {}
	for key, (desc, headPath, text) in letters.iteritems():
		if "/" in headPath:
			head, subhead = headPath.split("/", 1)
		else:
			head, subhead = headPath, None
		dictForHead = lettersDict.setdefault(head, {})
		dictForHead.setdefault(subhead, []).append((desc, key, text))
	return lettersDict


def _formatOneSelectionBlock(head, selectionDict):
	"""formatiert ein Unter-Dict aus _getLetterDict in ein HTML-Fragment.

	Ein Helfer fÃ¼r getLetterMenu.
	"""
	thisFragment = [u"<h2 class='lol'>%s</h2>"%head]
	for subhead, letters in sorted(selectionDict.iteritems()):
		if subhead is not None:
			thisFragment.append(u"<h3 class='lol'>%s</h3>"%subhead)
		letters.sort()

		for desc, key, text in letters:
			if text is None:
				thisFragment.append(u'<p class="lol">'
					'<input type="checkbox" name="letterKeys"'
					' value="%s" disabled> %s<sup><a href="#rem1">1</a></sup></p>'%(
					key, desc))

			elif desc.endswith(")"):
				name, remarks = parseRemarks(desc)
				thisFragment.append(u'<p class="lol">'
					'<input type="checkbox" name="letterKeys"'
					' value="%s"> %s %s</p>'%(
					key, name, remarks))

			else:
				thisFragment.append(u'<p class="lol">'
					'<input type="checkbox" name="letterKeys"'
					' value="%s"> %s</p>'%(key, desc))

	return u"<div class='lolbox'>%s</div>"%"\n".join(thisFragment)


def _getSelectionDict():
	"""gibt ein dict zurÃ¼ck, das Kategorien in LETTERs auf HTML zu deren
	Auswahl mappt.
	"""
	return dict((toplevel, _formatOneSelectionBlock(toplevel, secondLevelDict))
		for toplevel, secondLevelDict in _getLetterDict(LETTERS).iteritems())


def getForm(vars):
	fillers = {
		'scriptName': os.environ["SCRIPT_NAME"],
		'selection':
			Template(LETTER_MENU_TEMPLATE).render(_getSelectionDict())}
	fillers.update(vars)

	return Template(FORM_TEMPLATE).render(fillers)


def outputForm():
	vars = {
		"preBla": PRE_BLA,
		"postBla": POST_BLA,}

	if os.environ.get("HTTPS")!="on":
		vars["httpWarning"] = u"""
			<p class="warning">Es sieht aus, als wÃ¼rdest du Ã¼ber normales HTTP
			auf diesen Dienst zugreifen. HTTP
			ist ein unverschlÃ¼sseltes Protokoll, das, je nach Netzwerk,
			das Mitlesen ziemlich leicht macht.  Deutlich mehr Vertraulichkeit
			bietet <a href="%s">unser Dienst Ã¼ber HTTPS</a> (das die Daten
			zwischen deinem Browser und uns verschlÃ¼sselt).</p>"""%(
				escapeAttrVal("https://%s%s"%(
					os.environ["SERVER_NAME"],
					os.environ["SCRIPT_NAME"])))

	Template(BASE_TEMPLATE).serve(vars)


def _makeCleanForTeX():
	import string
	activeChars = u'"&~_${}#^%\\'
	nukeActives = dict((c, ' ') for c in activeChars)
	return lambda val: val.decode("utf-8", "ignore"
		).translate(nukeActives)

_cleanForTeX = _makeCleanForTeX()


def interpretForm():
	fieldSizes = {"vorname":25, "nachname":40, "ort":30, "adresse":50, 
		"plz":5, "gebdat":15, "gebort":30}
	cgiVals = cgi.FieldStorage()
	userRec = {"haveBackAddress": "yes"}

	for field, fieldSize in fieldSizes.items():
		userRec[field] = _cleanForTeX(
			cgiVals.getfirst(field, ""))
		if userRec[field]=="":
			userRec[field] = (
				r"\hbox spread %dex{\vrule height 17pt width0pt"
				r"\leaders\hrule\hfil}"%(2*fieldSize/3+1))
			userRec["haveBackAddress"] = "no"

	if not cgiVals.has_key("letterKeys"):
		httpFatalError(
			u"Du hast nicht ausgesucht, welche Briefe du haben mÃ¶chtest.")

	pdfData = makePdf(userRec, cgiVals.getlist("letterKeys"))
	sys.stdout.write("content-type: application/pdf\r\n")
	sys.stdout.write("content-length: %d\r\n\r\n"%len(pdfData))
	sys.stdout.write(pdfData)


def _test():
	rec = {
	"vorname": "Herbert",
	"nachname": u"MarcÃ¼se",
	"ort": "La Jolla",
	"adresse": "28 Sunshine Drive",
	"plz": "99121",
	"gebdat": "4.6.1869",
	"gebort": "Frankfurt",
	"haveBackAddress": "yes",
	}
	keys = ["bka", "lkabawu"]
	#keys = LETTERS
	open("result.pdf", "w").write(makePdf(rec, keys))


def main():
	if "SERVER_SOFTWARE" not in os.environ:
		_test()
		sys.exit(0)
	try:
		if os.environ.get("REQUEST_METHOD")=="POST":
			interpretForm()
		else:
			outputForm()
	except Error, msg:
		httpFatalError(unicode(msg))


if __name__=="__main__":
	try:
		main()
	except Exception, msg:
		import traceback
		traceback.print_exc()
		httpFatalError(unicode(msg))

# vi:ts=2:tw=72
