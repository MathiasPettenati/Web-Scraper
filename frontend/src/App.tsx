import { useEffect, useMemo, useState } from 'react';

type Product = {
  id: string;
  title: string;
  brand: string;
  category: string;
  color: string;
  condition: string;
  store: string;
  country: string;
  currency: string;
  price: number;
  original_price: number;
  discount_percent: number;
  sizes: string[];
  shipping_cost: number;
  shipping_time: string;
  rating: number;
  popularity: number;
  in_stock: boolean;
  verified: boolean;
  availability: string;
  source_url: string;
  last_verified: string;
  image_url: string;
  description: string;
  tags: string[];
  location_hint: string;
  deal_score: number;
};

type FilterPayload = {
  brands: string[];
  countries: string[];
  stores: string[];
  categories: string[];
  colors: string[];
  sizes: string[];
};

function formatMoney(value: number, currency = 'USD') {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value);
}

export default function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [products, setProducts] = useState<Product[]>([]);
  const [featured, setFeatured] = useState<Product[]>([]);
  const [filters, setFilters] = useState<FilterPayload | null>(null);
  const [query, setQuery] = useState('');
  const [country, setCountry] = useState('United States');
  const [category, setCategory] = useState('');
  const [brand, setBrand] = useState('');
  const [size, setSize] = useState('');
  const [color, setColor] = useState('');
  const [store, setStore] = useState('');
  const [condition, setCondition] = useState('');
  const [availability, setAvailability] = useState('');
  const [sort, setSort] = useState('best_deal');
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('deal-theme');
    if (storedTheme === 'light' || storedTheme === 'dark') {
      setTheme(storedTheme);
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    window.localStorage.setItem('deal-theme', theme);
  }, [theme]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [productsRes, featuredRes, filtersRes] = await Promise.all([
        fetch(`/api/deals?query=${encodeURIComponent(query)}&country=${encodeURIComponent(country)}&category=${encodeURIComponent(category)}&brand=${encodeURIComponent(brand)}&size=${encodeURIComponent(size)}&color=${encodeURIComponent(color)}&store=${encodeURIComponent(store)}&condition=${encodeURIComponent(condition)}&availability=${encodeURIComponent(availability)}&sort=${sort}&page=1&limit=12`),
        fetch('/api/deals/featured'),
        fetch('/api/deals/filters'),
      ]);
      const [productsJson, featuredJson, filtersJson] = await Promise.all([
        productsRes.json(),
        featuredRes.json(),
        filtersRes.json(),
      ]);
      setProducts(productsJson.items ?? []);
      setFeatured(featuredJson ?? []);
      setFilters(filtersJson);
      setLoading(false);
    };
    load();
  }, [query, country, category, brand, size, color, store, condition, availability, sort]);

  const bestDeal = useMemo(() => products[0], [products]);
  const dark = theme === 'dark';
  const shellClass = dark
    ? 'min-h-screen bg-[linear-gradient(135deg,#24001a_0%,#8a005d_48%,#ff6a00_100%)] text-orange-50 transition-colors duration-300'
    : 'min-h-screen bg-[linear-gradient(135deg,#fff1d6_0%,#ffb45f_48%,#ff2da8_100%)] text-[#3b071f] transition-colors duration-300';
  const panelClass = dark
    ? 'border border-[#ff7a18]/45 bg-[#3b0628]/92 shadow-xl shadow-pink-950/30'
    : 'border border-[#ff8a00]/45 bg-[#fff7e8] shadow-xl shadow-orange-300/20';
  const insetPanelClass = dark
    ? 'border border-[#ff2da8]/35 bg-[#270016]/88'
    : 'border border-[#ff7a18]/45 bg-[#ffe5bd]';
  const fieldClass = dark
    ? 'w-full border border-[#ff7a18]/45 bg-[#1f0014] px-3 py-2 text-sm text-orange-50 outline-none focus:border-[#ff2da8]'
    : 'w-full border border-[#ff8a00]/50 bg-[#fffaf0] px-3 py-2 text-sm text-[#3b071f] outline-none focus:border-[#ff2da8]';
  const mutedClass = dark ? 'text-orange-200/75' : 'text-[#8a3d20]';
  const eyebrowClass = dark
    ? 'text-sm font-semibold uppercase tracking-[0.28em] text-[#ff9f1c]'
    : 'text-sm font-semibold uppercase tracking-[0.28em] text-[#d44686]';
  const primaryButtonClass = dark
    ? 'border border-[#ffb347] bg-[#ff7a18] px-4 py-2 font-semibold text-[#24001a] hover:bg-[#ff9f1c]'
    : 'border border-[#c7277a] bg-[#ff2da8] px-4 py-2 font-semibold text-white hover:bg-[#ff7a18]';
  const secondaryButtonClass = dark
    ? 'border border-[#ff2da8]/45 bg-[#270016] px-4 py-2 text-sm font-medium text-orange-50 hover:border-[#ff7a18]'
    : 'border border-[#ff7a18]/55 bg-[#fff1d6] px-4 py-2 text-sm font-medium text-[#3b071f] hover:border-[#ff2da8]';
  const productImageClass = dark
    ? 'aspect-square w-full border border-[#ff7a18]/45 bg-[#fff1d6] object-contain'
    : 'aspect-square w-full border border-[#ff2da8]/35 bg-[#fff8e8] object-contain';
  const productImageBorderClass = dark
    ? 'aspect-square w-full border-b border-[#ff7a18]/45 bg-[#fff1d6] object-contain'
    : 'aspect-square w-full border-b border-[#ff2da8]/35 bg-[#fff8e8] object-contain';

  return (
    <div className={shellClass}>
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <header className={`${panelClass} p-4 md:p-6`}>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className={eyebrowClass}>Women's clothing deals</p>
              <h1 className="text-3xl font-semibold sm:text-4xl">Find the best discounts across trusted retailers.</h1>
              <p className={`mt-2 max-w-2xl text-sm sm:text-base ${mutedClass}`}>
                Search, compare, and save standout offers with transparent shipping, verified listings, and fast local recommendations.
              </p>
            </div>
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className={secondaryButtonClass}
            >
              {theme === 'dark' ? 'Light mode' : 'Dark mode'}
            </button>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.45fr_0.8fr]">
          <div className={`${panelClass} p-4 sm:p-6`}>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <label className="flex-1">
                <span className={`mb-2 block text-sm font-medium ${mutedClass}`}>Search</span>
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search dresses, jackets, jeans..."
                  className={fieldClass}
                />
              </label>
              <label>
                <span className={`mb-2 block text-sm font-medium ${mutedClass}`}>Country</span>
                <select
                  value={country}
                  onChange={(event) => setCountry(event.target.value)}
                  className={fieldClass}
                >
                  <option>United States</option>
                  <option>Canada</option>
                  <option>United Kingdom</option>
                  <option>Australia</option>
                  <option>Germany</option>
                  <option>France</option>
                  <option>Japan</option>
                </select>
              </label>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <label>
                <span className={`mb-2 block text-sm ${mutedClass}`}>Category</span>
                <select value={category} onChange={(event) => setCategory(event.target.value)} className={fieldClass}>
                  <option value="">Any</option>
                  {filters?.categories.map((entry) => <option key={entry}>{entry}</option>)}
                </select>
              </label>
              <label>
                <span className={`mb-2 block text-sm ${mutedClass}`}>Brand</span>
                <select value={brand} onChange={(event) => setBrand(event.target.value)} className={fieldClass}>
                  <option value="">Any</option>
                  {filters?.brands.map((entry) => <option key={entry}>{entry}</option>)}
                </select>
              </label>
              <label>
                <span className={`mb-2 block text-sm ${mutedClass}`}>Size</span>
                <select value={size} onChange={(event) => setSize(event.target.value)} className={fieldClass}>
                  <option value="">Any</option>
                  {filters?.sizes.map((entry) => <option key={entry}>{entry}</option>)}
                </select>
              </label>
              <label>
                <span className={`mb-2 block text-sm ${mutedClass}`}>Sort</span>
                <select value={sort} onChange={(event) => setSort(event.target.value)} className={fieldClass}>
                  <option value="best_deal">Best overall deal</option>
                  <option value="lowest_price">Lowest price</option>
                  <option value="highest_discount">Highest discount</option>
                  <option value="newest">Newest listing</option>
                  <option value="popularity">Popularity</option>
                  <option value="rating">Highest rating</option>
                  <option value="fastest_delivery">Fastest delivery</option>
                </select>
              </label>
            </div>
          </div>

          <aside className={`${panelClass} p-4`}>
            <p className={eyebrowClass}>Best deal</p>
            {bestDeal ? (
              <>
                <img src={bestDeal.image_url} alt={bestDeal.title} className={`mt-4 ${productImageClass}`} />
                <h2 className="mt-4 text-xl font-semibold">{bestDeal.title}</h2>
                <p className={`mt-1 text-sm ${mutedClass}`}>{bestDeal.brand} - {bestDeal.store}</p>
                <div className="mt-4 flex items-end justify-between gap-3">
                  <div>
                    <p className="text-2xl font-semibold">{formatMoney(bestDeal.price, bestDeal.currency)}</p>
                    <p className={`text-sm ${mutedClass}`}>was {formatMoney(bestDeal.original_price, bestDeal.currency)}</p>
                  </div>
                  <span className={`${insetPanelClass} px-3 py-1 text-sm font-medium`}>{bestDeal.discount_percent}% off</span>
                </div>
                <button
                  onClick={() => setSelectedProduct(bestDeal)}
                  className={`mt-4 w-full ${primaryButtonClass}`}
                >
                  View details
                </button>
              </>
            ) : (
              <p className={`mt-3 text-sm ${mutedClass}`}>Adjust the filters to reveal more offers.</p>
            )}
          </aside>
        </section>

        <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div className={`${panelClass} p-4`}>
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className={eyebrowClass}>Nearby and local</p>
                <h3 className="text-xl font-semibold">Local pickup and nearby stores</h3>
              </div>
              <button
                onClick={() => {
                  if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(() => window.alert('Location permission granted. Nearby recommendations are ready.'));
                  }
                }}
                className={secondaryButtonClass}
              >
                Use my location
              </button>
            </div>
            <div className="mt-4 space-y-3">
              <div className={`${insetPanelClass} p-3`}>
                <p className="font-medium">Downtown Pickup Hub</p>
                <p className={`mt-1 text-sm ${mutedClass}`}>3.2 km away - Same-day pickup available</p>
              </div>
              <div className={`${insetPanelClass} p-3`}>
                <p className="font-medium">Local Retail Annex</p>
                <p className={`mt-1 text-sm ${mutedClass}`}>5.8 km away - Free pickup on orders over $75</p>
              </div>
            </div>
          </div>

          <div className={`${panelClass} p-4`}>
            <div className="flex items-center justify-between">
              <div>
                <p className={eyebrowClass}>Best deals</p>
                <h3 className="text-xl font-semibold">Ranked by price, shipping, rating, and reliability</h3>
              </div>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {featured.map((item) => (
                <div key={item.id} className={`${insetPanelClass} p-3`}>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium">{item.title}</p>
                      <p className={`text-sm ${mutedClass}`}>{item.store} - {item.country}</p>
                    </div>
                    <span className="border border-[#ff2da8]/45 bg-[#ff7a18]/15 px-2 py-1 text-xs font-medium">{item.discount_percent}%</span>
                  </div>
                  <p className={`mt-2 text-sm ${mutedClass}`}>{formatMoney(item.price, item.currency)} - {item.shipping_cost === 0 ? 'Free shipping' : `Shipping ${formatMoney(item.shipping_cost, item.currency)}`}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className={`${panelClass} p-4 sm:p-6`}>
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <p className={eyebrowClass}>Catalog</p>
              <h3 className="text-xl font-semibold">Curated women's fashion deals</h3>
            </div>
            <p className={`text-sm ${mutedClass}`}>Verified - In stock - Price drop friendly</p>
          </div>
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, index) => <div key={index} className="h-56 animate-pulse bg-[#ff7a18]/25" />)}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {products.map((product) => (
                <article key={product.id} className={`${insetPanelClass} overflow-hidden transition-transform duration-200 hover:-translate-y-1`}>
                  <img src={product.image_url} alt={product.title} className={productImageBorderClass} />
                  <div className="p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className={`text-sm font-semibold ${mutedClass}`}>{product.brand}</p>
                        <h4 className="text-lg font-semibold">{product.title}</h4>
                      </div>
                      <span className="border border-[#ff2da8]/45 bg-[#ff7a18]/15 px-2 py-1 text-xs font-medium">{product.discount_percent}%</span>
                    </div>
                    <p className={`mt-2 text-sm ${mutedClass}`}>{product.description}</p>
                    <div className="mt-3 flex items-center justify-between gap-4 text-sm">
                      <div>
                        <p className="font-semibold">{formatMoney(product.price, product.currency)}</p>
                        <p className={`${mutedClass} line-through`}>{formatMoney(product.original_price, product.currency)}</p>
                      </div>
                      <div className={`text-right ${mutedClass}`}>
                        <p>{product.store}</p>
                        <p>{product.shipping_cost === 0 ? 'Free shipping' : formatMoney(product.shipping_cost, product.currency)}</p>
                      </div>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {product.sizes.slice(0, 4).map((entry) => <span key={entry} className="border border-[#ff7a18]/45 px-2 py-1 text-xs">{entry}</span>)}
                    </div>
                    <div className="mt-4 flex gap-2">
                      <button onClick={() => setSelectedProduct(product)} className={`flex-1 ${secondaryButtonClass}`}>
                        View details
                      </button>
                      <a href={product.source_url} target="_blank" rel="noreferrer" className={`flex-1 text-center ${primaryButtonClass}`}>
                        Open product
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>

      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
          <div className={`w-full max-w-3xl ${panelClass} p-5`}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className={eyebrowClass}>Product details</p>
                <h3 className="text-2xl font-semibold">{selectedProduct.title}</h3>
              </div>
              <button onClick={() => setSelectedProduct(null)} className={secondaryButtonClass}>Close</button>
            </div>
            <div className="mt-4 grid gap-6 md:grid-cols-[1fr_0.9fr]">
              <img src={selectedProduct.image_url} alt={selectedProduct.title} className={productImageClass} />
              <div>
                <p className={`text-sm ${mutedClass}`}>{selectedProduct.brand} - {selectedProduct.store}</p>
                <p className={`mt-2 text-sm ${mutedClass}`}>{selectedProduct.description}</p>
                <div className={`mt-4 ${insetPanelClass} p-4`}>
                  <p className="text-3xl font-semibold">{formatMoney(selectedProduct.price, selectedProduct.currency)}</p>
                  <p className={`${mutedClass} text-sm line-through`}>{formatMoney(selectedProduct.original_price, selectedProduct.currency)}</p>
                  <p className={`mt-2 text-sm ${mutedClass}`}>{selectedProduct.discount_percent}% off - {selectedProduct.shipping_cost === 0 ? 'Free shipping' : formatMoney(selectedProduct.shipping_cost, selectedProduct.currency)}</p>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {selectedProduct.sizes.map((entry) => <span key={entry} className="border border-[#ff7a18]/45 px-2 py-1 text-sm">{entry}</span>)}
                </div>
                <div className="mt-4 flex flex-col gap-2">
                  <a href={selectedProduct.source_url} target="_blank" rel="noreferrer" className={`text-center ${primaryButtonClass}`}>
                    Open product page
                  </a>
                  <button className={secondaryButtonClass}>Save product</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
