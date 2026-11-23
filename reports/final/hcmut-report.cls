\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hcmut-report}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[12pt,a4paper]{article}

\RequirePackage[utf8]{vntex,inputenc}
\RequirePackage{anyfontsize,amsmath,amssymb}
\RequirePackage[T5]{fontenc}

\RequirePackage{geometry,graphicx,indentfirst,setspace}
\RequirePackage{booktabs}
\RequirePackage[center]{caption}

\RequirePackage{fancyhdr,hyperref}
\RequirePackage[super,square,sort]{natbib}

% Change to '[english,vietnamese]' to use Vietnamese labels
\RequirePackage[english,vietnamese]{babel}

% Custom commands
\newcommand{\Month}{Tháng \the\month\ năm }

\newcommand{\@upperuniname}{Đại học Quốc gia Thành phố Hồ Chí Minh}
\newcommand{\@uniname}{Trường Đại học Bách khoa}

\newcommand{\@deptname}{Khoa Khoa học và Kỹ thuật Máy tính}
\newcommand{\deptname}[1]{\renewcommand{\@deptname}{#1}}

\newcommand{\@coursename}{Tên học phần}
\newcommand{\coursename}[1]{\renewcommand{\@coursename}{#1}}

\newcommand{\@reporttype}{Báo cáo Bài tập lớn}
\newcommand{\reporttype}[1]{\renewcommand{\@reporttype}{#1}}

\renewcommand{\@title}{Tên báo cáo}

\newcommand{\@advisor}{Giảng viên hướng dẫn}
\newcommand{\advisor}[1]{\renewcommand{\@advisor}{#1}}

\newcommand{\@stuname}{SVTH}
\newcommand{\stuname}[1]{\renewcommand{\@stuname}{#1}}

\newcommand{\@reportplace}{TP. Hồ Chí Minh}
\newcommand{\reportplace}[1]{\renewcommand{\@reportplace}{#1}}

\newcommand{\@reporttime}{\Month \the\year}
\newcommand{\reporttime}[1]{\renewcommand{\@reporttime}{#1}}

% Configurations
%\graphicspath{{subdir1/}{subdir2/}{subdir3/}...{subdirn/}}

\geometry{
  paper=a4paper,
  left=3cm,
  right=2cm,
  vmargin=2cm,
  includeheadfoot=true,
  headheight=35pt
}

\onehalfspacing
\raggedbottom
\renewcommand{\arraystretch}{1.2}

\setlength{\parindent}{1.27cm}
\setlength{\parskip}{3pt plus 1pt minus 1pt}

% Format paragraph as display heading (level 4, with line break and bold)
\renewcommand{\paragraph}{%
  \@startsection{paragraph}{4}{\z@}%
  {1.5ex \@plus 0.5ex \@minus 0.2ex}%
  {0.5ex \@plus 0.2ex}%
  {\normalfont\normalsize\bfseries}%
}

% Set depth of numbering for sections and table of contents
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}

% Set depth of numbering for counters
\AtBeginDocument{\counterwithin{equation}{section}}
\AtBeginDocument{\counterwithin{table}{section}}
\AtBeginDocument{\counterwithin{figure}{section}}

\AtBeginDocument{\renewcommand*\bibname{Tài liệu tham khảo}}

\hypersetup{
  colorlinks=true,
  linkcolor=black,
  citecolor=red,
  urlcolor=blue
}

\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}

\pagestyle{fancy}
\fancyhf{}

%\renewcommand{\subsectionmark}[1]{\markright{\thesubsection.\ #1}}

% The drawing units are interpreted as multiples of \unitlength
% unless a unit is given
%\setlength{\unitlength}{1pt}

\fancyhead[L]{
  \bfseries
  \begin{tabular}{rl}
    \begin{picture}(25pt,15pt)
      \put(0,-8pt){\includegraphics[width=20pt]{graphics/hcmut.png}}
    \end{picture}
    \begin{tabular}{l}
      \ttfamily\@uniname \\
      \ttfamily\@deptname \\
    \end{tabular}
  \end{tabular}
}

\fancyfoot[C]{\thepage}

% Custom pages and sections
\newcommand{\coverpage}{
  \pagestyle{empty}

  \vspace*{-3\baselineskip}
  \begin{center}
    \MakeUppercase{\@upperuniname}

    \MakeUppercase{\@uniname}

    \MakeUppercase{\@deptname}
    \vfill
    \includegraphics[scale=0.4]{graphics/hcmut.png}
    \vfill
    \bfseries
    \begin{tabular}{c}
      \toprule
      {}                                                 \\
      \Large\@reporttype                                 \\
      {}                                                 \\
      \Huge\parbox[c]{0.8\linewidth}{\centering \@title} \\
      {}                                                 \\
      \bottomrule
    \end{tabular}
    \vfill
    \mdseries
    \begin{tabular}{rll}
      GVHD: \@advisor \\
      SVTH: \@stuname \\
    \end{tabular}
    \vfill
    \MakeUppercase{\@reportplace, \@reporttime}
  \end{center}

  \cleardoublepage
  \pagestyle{fancy}
}
